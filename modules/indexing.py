from modules import app, q, es, bucket
from flask import abort, request
import mdtraj as md
import boto
import uuid
import os

_AMINO_ACID_CODES =  {'ACE': None, 'NME':  None, '00C': 'C', '01W':  'X', '02K':
'A', '02L':  'N', '03Y': 'C',  '07O': 'C', '08P':  'C', '0A0': 'D',  '0A1': 'Y',
'0A2': 'K', '0A8':  'C', '0AA': 'V', '0AB': 'V', '0AC':  'G', '0AF': 'W', '0AG':
'L', '0AH':  'S', '0AK': 'D',  '0BN': 'F', '0CS':  'A', '0E5': 'T',  '0EA': 'Y',
'0FL': 'A', '0NC':  'A', '0WZ': 'Y', '0Y8': 'P', '143':  'C', '193': 'X', '1OP':
'Y', '1PA':  'F', '1PI': 'A',  '1TQ': 'W', '1TY':  'Y', '1X6': 'S',  '200': 'F',
'23F': 'F', '23S':  'X', '26B': 'T', '2AD': 'X', '2AG':  'A', '2AO': 'X', '2AS':
'X', '2CO':  'C', '2DO': 'X',  '2FM': 'M', '2HF':  'H', '2KK': 'K',  '2KP': 'K',
'2LU': 'L', '2ML':  'L', '2MR': 'R', '2MT': 'P', '2OR':  'R', '2PI': 'X', '2QZ':
'T', '2R3':  'Y', '2SI': 'X',  '2TL': 'T', '2TY':  'Y', '2VA': 'V',  '2XA': 'C',
'32S': 'X', '32T':  'X', '33X': 'A', '3AH': 'H', '3AR':  'X', '3CF': 'F', '3GA':
'A', '3MD':  'D', '3NF': 'Y',  '3QN': 'K', '3TY':  'X', '3XH': 'G',  '4BF': 'Y',
'4CF': 'F', '4CY':  'M', '4DP': 'W', '4FB': 'P', '4FW':  'W', '4HT': 'W', '4IN':
'W', '4MM':  'X', '4PH': 'F',  '4U7': 'A', '56A':  'H', '5AB': 'A',  '5CS': 'C',
'5CW': 'W', '5HP':  'E', '6CL': 'K', '6CW': 'W', '6GL':  'A', '6HN': 'K', '7JA':
'I', '9NE':  'E', '9NF': 'F',  '9NR': 'R', '9NV':  'V', 'A5N': 'N',  'A66': 'X',
'AA3': 'A', 'AA4':  'A', 'AAR': 'R', 'AB7': 'X', 'ABA':  'A', 'ACB': 'D', 'ACL':
'R', 'ADD':  'X', 'AEA': 'X',  'AEI': 'D', 'AFA':  'N', 'AGM': 'R',  'AGT': 'C',
'AHB': 'N', 'AHH':  'X', 'AHO': 'A', 'AHP': 'A', 'AHS':  'X', 'AHT': 'X', 'AIB':
'A', 'AKL':  'D', 'AKZ': 'D',  'ALA': 'A', 'ALC':  'A', 'ALM': 'A',  'ALN': 'A',
'ALO': 'T', 'ALS':  'A', 'ALT': 'A', 'ALV': 'A', 'ALY':  'K', 'AN8': 'A', 'APE':
'X', 'APH':  'A', 'API': 'K',  'APK': 'K', 'APM':  'X', 'APP': 'X',  'AR2': 'R',
'AR4': 'E', 'AR7':  'R', 'ARG': 'R', 'ARM': 'R', 'ARO':  'R', 'ARV': 'X', 'AS2':
'D', 'AS9':  'X', 'ASA': 'D',  'ASB': 'D', 'ASI':  'D', 'ASK': 'D',  'ASL': 'D',
'ASM': 'X', 'ASN':  'N', 'ASP': 'D', 'ASQ': 'D', 'ASX':  'B', 'AVN': 'X', 'AYA':
'A', 'AZK':  'K', 'AZS': 'S',  'AZY': 'Y', 'B1F':  'F', 'B2A': 'A',  'B2F': 'F',
'B2I': 'I', 'B2V':  'V', 'B3A': 'A', 'B3D': 'D', 'B3E':  'E', 'B3K': 'K', 'B3L':
'X', 'B3M':  'X', 'B3Q': 'X',  'B3S': 'S', 'B3T':  'X', 'B3U': 'H',  'B3X': 'N',
'B3Y': 'Y', 'BB6':  'C', 'BB7': 'C', 'BB8': 'F', 'BB9':  'C', 'BBC': 'C', 'BCS':
'C', 'BE2':  'X', 'BFD': 'D',  'BG1': 'S', 'BH2':  'D', 'BHD': 'D',  'BIF': 'F',
'BIL': 'X', 'BIU':  'I', 'BJH': 'X', 'BL2': 'L', 'BLE':  'L', 'BLY': 'K', 'BMT':
'T', 'BNN':  'F', 'BNO': 'X',  'BOR': 'R', 'BPE':  'C', 'BSE': 'S',  'BTA': 'L',
'BTC': 'C', 'BTR':  'W', 'BUC': 'C', 'BUG': 'V', 'C1X':  'K', 'C22': 'A', 'C3Y':
'C', 'C4R':  'C', 'C5C': 'C',  'C66': 'X', 'C6C':  'C', 'CAF': 'C',  'CAL': 'X',
'CAS': 'C', 'CAV':  'X', 'CAY': 'C', 'CCL': 'K', 'CCS':  'C', 'CDE': 'X', 'CDV':
'X', 'CEA':  'C', 'CGA': 'E',  'CGU': 'E', 'CHF':  'X', 'CHG': 'X',  'CHP': 'G',
'CHS': 'X', 'CIR':  'R', 'CLE': 'L', 'CLG': 'K', 'CLH':  'K', 'CME': 'C', 'CMH':
'C', 'CML':  'C', 'CMT': 'C',  'CPC': 'X', 'CPI':  'X', 'CR5': 'G',  'CS0': 'C',
'CS1': 'C', 'CS3':  'C', 'CS4': 'C', 'CSA': 'C', 'CSB':  'C', 'CSD': 'C', 'CSE':
'C', 'CSJ':  'C', 'CSO': 'C',  'CSP': 'C', 'CSR':  'C', 'CSS': 'C',  'CSU': 'C',
'CSW': 'C', 'CSX':  'C', 'CSZ': 'C', 'CTE': 'W', 'CTH':  'T', 'CUC': 'X', 'CWR':
'S', 'CXM':  'M', 'CY0': 'C',  'CY1': 'C', 'CY3':  'C', 'CY4': 'C',  'CYA': 'C',
'CYD': 'C', 'CYF':  'C', 'CYG': 'C', 'CYJ': 'K', 'CYM':  'C', 'CYQ': 'C', 'CYR':
'C', 'CYS':  'C', 'CZ2': 'C',  'CZZ': 'C', 'D11':  'T', 'D3P': 'G',  'D4P': 'X',
'DA2': 'X', 'DAB':  'A', 'DAH': 'F', 'DAL': 'A', 'DAR':  'R', 'DAS': 'D', 'DBB':
'T', 'DBS':  'S', 'DBU': 'T',  'DBY': 'Y', 'DBZ':  'A', 'DC2': 'C',  'DCL': 'X',
'DCY': 'C', 'DDE':  'H', 'DFI': 'X', 'DFO': 'X', 'DGH':  'G', 'DGL': 'E', 'DGN':
'Q', 'DHA':  'S', 'DHI': 'H',  'DHL': 'X', 'DHN':  'V', 'DHP': 'X',  'DHV': 'V',
'DI7': 'Y', 'DIL':  'I', 'DIR': 'R', 'DIV': 'V', 'DLE':  'L', 'DLS': 'K', 'DLY':
'K', 'DM0':  'K', 'DMH': 'N',  'DMK': 'D', 'DMT':  'X', 'DNE': 'L',  'DNL': 'K',
'DNP': 'A', 'DNS':  'K', 'DOA': 'X', 'DOH': 'D', 'DON':  'L', 'DPL': 'P', 'DPN':
'F', 'DPP':  'A', 'DPQ': 'Y',  'DPR': 'P', 'DSE':  'S', 'DSG': 'N',  'DSN': 'S',
'DSP': 'D', 'DTH':  'T', 'DTR': 'W', 'DTY': 'Y', 'DVA':  'V', 'DYS': 'C', 'ECC':
'Q', 'EFC':  'C', 'EHP': 'F',  'ESB': 'Y', 'ESC':  'M', 'EXY': 'L',  'EYS': 'X',
'F2F': 'F', 'FAK':  'K', 'FB5': 'A', 'FB6': 'A', 'FCL':  'F', 'FGA': 'E', 'FGL':
'G', 'FGP':  'S', 'FH7': 'K',  'FHL': 'K', 'FHO':  'K', 'FLA': 'A',  'FLE': 'L',
'FLT': 'Y', 'FME':  'M', 'FOE': 'C', 'FP9': 'P', 'FRD':  'X', 'FT6': 'W', 'FTR':
'W', 'FTY':  'Y', 'FVA': 'V',  'FZN': 'K', 'GAU':  'E', 'GCM': 'X',  'GFT': 'S',
'GGL': 'E', 'GHG':  'Q', 'GHP': 'G', 'GL3': 'G', 'GLH':  'Q', 'GLJ': 'E', 'GLK':
'E', 'GLM':  'X', 'GLN': 'Q',  'GLQ': 'E', 'GLU':  'E', 'GLX': 'Z',  'GLY': 'G',
'GLZ': 'G', 'GMA':  'E', 'GND': 'X', 'GPL': 'K', 'GSC':  'G', 'GSU': 'E', 'GT9':
'C', 'GVL':  'S', 'H14': 'F',  'H5M': 'P', 'HAC':  'A', 'HAR': 'R',  'HBN': 'H',
'HCS': 'X', 'HFA':  'X', 'HGL': 'X', 'HHI': 'H', 'HIA':  'H', 'HIC': 'H', 'HIP':
'H', 'HIQ':  'H', 'HIS': 'H',  'HL2': 'L', 'HLU':  'L', 'HMR': 'R',  'HPC': 'F',
'HPE': 'F', 'HPH':  'F', 'HPQ': 'F', 'HQA': 'A', 'HRG':  'R', 'HRP': 'W', 'HS8':
'H', 'HS9':  'H', 'HSE': 'S',  'HSL': 'S', 'HSO':  'H', 'HTI': 'C',  'HTN': 'N',
'HTR': 'W', 'HV5':  'A', 'HVA': 'V', 'HY3': 'P', 'HYP':  'P', 'HZP': 'P', 'I2M':
'I', 'I58':  'K', 'IAM': 'A',  'IAR': 'R', 'IAS':  'D', 'IEL': 'K',  'IGL': 'G',
'IIL': 'I', 'ILE':  'I', 'ILG': 'E', 'ILX': 'I', 'IML':  'I', 'IOY': 'F', 'IPG':
'G', 'IT1':  'K', 'IYR': 'Y',  'IYT': 'T', 'IZO':  'M', 'JJJ': 'C',  'JJK': 'C',
'JJL': 'C', 'K1R':  'C', 'KCX': 'K', 'KGC': 'K', 'KNB':  'A', 'KOR': 'M', 'KPI':
'K', 'KST':  'K', 'KYN': 'W',  'KYQ': 'K', 'L2A':  'X', 'LA2': 'K',  'LAA': 'D',
'LAL': 'A', 'LBY':  'K', 'LCK': 'K', 'LCX': 'K', 'LCZ':  'X', 'LDH': 'K', 'LED':
'L', 'LEF':  'L', 'LEH': 'L',  'LEI': 'V', 'LEM':  'L', 'LEN': 'L',  'LET': 'K',
'LEU': 'L', 'LEX':  'L', 'LHC': 'X', 'LLP': 'K', 'LLY':  'K', 'LME': 'E', 'LMF':
'K', 'LMQ':  'Q', 'LP6': 'K',  'LPD': 'P', 'LPG':  'G', 'LPL': 'X',  'LPS': 'S',
'LSO': 'K', 'LTA':  'X', 'LTR': 'W', 'LVG': 'G', 'LVN':  'V', 'LYF': 'K', 'LYK':
'K', 'LYM':  'K', 'LYN': 'K',  'LYR': 'K', 'LYS':  'K', 'LYX': 'K',  'LYZ': 'K',
'M0H': 'C',  'M2L': 'K', 'M2S': 'M',  'M30': 'G', 'M3L': 'K',  'MA': 'A', 'MAA':
'A', 'MAI':  'R', 'MBQ': 'Y',  'MC1': 'S', 'MCG':  'X', 'MCL': 'K',  'MCS': 'C',
'MD3': 'C', 'MD6':  'G', 'MDF': 'Y', 'MDH': 'X', 'MEA':  'F', 'MED': 'M', 'MEG':
'E', 'MEN':  'N', 'MEQ': 'Q',  'MET': 'M', 'MEU':  'G', 'MF3': 'X',  'MGG': 'R',
'MGN': 'Q', 'MGY':  'G', 'MHL': 'L', 'MHO': 'M', 'MHS':  'H', 'MIS': 'S', 'MK8':
'L', 'ML3':  'K', 'MLE': 'L',  'MLL': 'L', 'MLY':  'K', 'MLZ': 'K',  'MME': 'M',
'MMO': 'R', 'MND':  'N', 'MNL': 'L', 'MNV': 'V', 'MOD':  'X', 'MP8': 'P', 'MPH':
'X', 'MPJ':  'X', 'MPQ': 'G',  'MSA': 'G', 'MSE':  'M', 'MSL': 'M',  'MSO': 'M',
'MSP': 'X', 'MT2':  'M', 'MTY': 'Y', 'MVA': 'V', 'N10':  'S', 'N2C': 'X', 'N7P':
'P', 'N80':  'P', 'N8P': 'P',  'NA8': 'A', 'NAL':  'A', 'NAM': 'A',  'NB8': 'N',
'NBQ': 'Y', 'NC1':  'S', 'NCB': 'A', 'NCY': 'X', 'NDF':  'F', 'NEM': 'H', 'NEP':
'H', 'NFA':  'F', 'NHL': 'E',  'NIY': 'Y', 'NLE':  'L', 'NLN': 'L',  'NLO': 'L',
'NLP': 'L', 'NLQ':  'Q', 'NMC': 'G', 'NMM': 'R', 'NNH':  'R', 'NPH': 'C', 'NPI':
'A', 'NSK':  'X', 'NTR': 'Y',  'NTY': 'Y', 'NVA':  'V', 'NYS': 'C',  'NZH': 'H',
'O12': 'X', 'OAR':  'R', 'OAS': 'S', 'OBF': 'X', 'OBS':  'K', 'OCS': 'C', 'OCY':
'C', 'OHI':  'H', 'OHS': 'D',  'OIC': 'X', 'OLE':  'X', 'OLT': 'T',  'OLZ': 'S',
'OMT': 'M', 'ONH':  'A', 'ONL': 'X', 'OPR': 'R', 'ORN':  'A', 'ORQ': 'R', 'OSE':
'S', 'OTB':  'X', 'OTH': 'T',  'OXX': 'D', 'P1L':  'C', 'P2Y': 'P',  'PAQ': 'Y',
'PAS': 'D', 'PAT':  'W', 'PAU': 'A', 'PBB': 'C', 'PBF':  'F', 'PCA': 'E', 'PCC':
'P', 'PCE':  'X', 'PCS': 'F',  'PDL': 'X', 'PEC':  'C', 'PF5': 'F',  'PFF': 'F',
'PFX': 'X', 'PG1':  'S', 'PG9': 'G', 'PGL': 'X', 'PGY':  'G', 'PH6': 'P', 'PHA':
'F', 'PHD':  'D', 'PHE': 'F',  'PHI': 'F', 'PHL':  'F', 'PHM': 'F',  'PIV': 'X',
'PLE': 'L', 'PM3':  'F', 'POM': 'P', 'PPN': 'F', 'PR3':  'C', 'PR9': 'P', 'PRO':
'P', 'PRS':  'P', 'PSA': 'F',  'PSH': 'H', 'PTA':  'X', 'PTH': 'Y',  'PTM': 'Y',
'PTR': 'Y', 'PVH':  'H', 'PVL': 'X', 'PYA': 'A', 'PYL':  'O', 'PYX': 'C', 'QCS':
'C', 'QMM':  'Q', 'QPA': 'C',  'QPH': 'F', 'R1A':  'C', 'R4K': 'W',  'RE0': 'W',
'RE3': 'W', 'RON':  'X', 'RVX': 'S', 'RZ4': 'S', 'S1H':  'S', 'S2C': 'C', 'S2D':
'A', 'S2P':  'A', 'SAC': 'S',  'SAH': 'C', 'SAR':  'G', 'SBL': 'S',  'SCH': 'C',
'SCS': 'C', 'SCY':  'C', 'SD2': 'X', 'SDP': 'S', 'SE7':  'A', 'SEB': 'S', 'SEC':
'U', 'SEG':  'A', 'SEL': 'S',  'SEM': 'S', 'SEN':  'S', 'SEP': 'S',  'SER': 'S',
'SET': 'S', 'SGB':  'S', 'SHC': 'C', 'SHP': 'G', 'SHR':  'K', 'SIB': 'C', 'SLR':
'P', 'SLZ':  'K', 'SMC': 'C',  'SME': 'M', 'SMF':  'F', 'SNC': 'C',  'SNN': 'N',
'SOC': 'C', 'SOY':  'S', 'SRZ': 'S', 'STY': 'Y', 'SUB':  'X', 'SUN': 'S', 'SVA':
'S', 'SVV':  'S', 'SVW': 'S',  'SVX': 'S', 'SVY':  'S', 'SVZ': 'S',  'SYS': 'C',
'T11': 'F', 'T66':  'X', 'TA4': 'X', 'TAV': 'D', 'TBG':  'V', 'TBM': 'T', 'TCQ':
'Y', 'TCR':  'W', 'TDD': 'L',  'TFQ': 'F', 'TH6':  'T', 'THC': 'T',  'THO': 'X',
'THR': 'T', 'THZ':  'R', 'TIH': 'A', 'TMB': 'T', 'TMD':  'T', 'TNB': 'C', 'TNR':
'S', 'TOQ':  'W', 'TPH': 'X',  'TPL': 'W', 'TPO':  'T', 'TPQ': 'Y',  'TQI': 'W',
'TQQ': 'W', 'TRF':  'W', 'TRG': 'K', 'TRN': 'W', 'TRO':  'W', 'TRP': 'W', 'TRQ':
'W', 'TRW':  'W', 'TRX': 'W',  'TRY': 'W', 'TST':  'X', 'TTQ': 'W',  'TTS': 'Y',
'TXY': 'Y', 'TY1':  'Y', 'TY2': 'Y', 'TY3': 'Y', 'TY5':  'Y', 'TYB': 'Y', 'TYI':
'Y', 'TYJ':  'Y', 'TYN': 'Y',  'TYO': 'Y', 'TYQ':  'Y', 'TYR': 'Y',  'TYS': 'Y',
'TYT': 'Y', 'TYW':  'Y', 'TYX': 'X', 'TYY': 'Y', 'TZB':  'X', 'TZO': 'X', 'UMA':
'A', 'UN1':  'X', 'UN2': 'X',  'UNK': 'X', 'VAD':  'V', 'VAF': 'V',  'VAL': 'V',
'VB1': 'K', 'VDL':  'X', 'VLL': 'X', 'VLM': 'X', 'VMS':  'X', 'VOL': 'X', 'WLU':
'L', 'WPA':  'F', 'WRP': 'W',  'WVL': 'V', 'X2W':  'E', 'XCN': 'C',  'XCP': 'X',
'XDT': 'T', 'XPL':  'O', 'XPR': 'P', 'XSN': 'N', 'XX1':  'K', 'YCM': 'C', 'YOF':
'Y', 'YTH':  'T', 'Z01': 'A',  'ZAL': 'A', 'ZCL':  'F', 'ZFB': 'X',  'ZU0': 'T',
'ZZJ': 'A'}


@app.route('/index/submit/', methods=['POST'])
def reindex():
    if request.method == 'POST':
        filename = request.form.get('filename', None)
        if filename is not None:
            id = start_reindex(filename)
            return '{id: ' + str(id) + '}', 200
        else:
            abort(401)
    else:
        abort(405)

@app.route('/index/status/<job_id>')
def check_status(job_id):
    job = q.fetch_job(job_id)

    if job is None:
        abort(404)

    if job.result is None:
        return '{status: "running"}'
    else:
        if job.result == 0:
            return '{status: "done"}'
        else:
            return '{status: "error"}'


def reindex_file(filename):
    filetype = filename.split('.')
    if len(filetype) != 2:
        return -1
    filetype = filetype[1]
    # grab the file from s3
    key = boto.s3.key.Key(bucket)
    temp_name = "/tmp/mddb/" + str(uuid.uuid4()) + '-' + filename
    key.key = filename
    key.get_contents_to_filename(temp_name)
    #try:
    traj = md.load(temp_name)
    #chains = [parse_chain(c) for c in traj.topology.chains]
    full_chains = [full_chain(c) for c in traj.topology.chains]
    short_chains = [short_name(c) for c in traj.topology.chains]
    residue_set = [all_residues(c) for c in traj.topology.chains]
    v = []
    for s in residue_set:
        v += list(s)
    es.index(index="mddb-index", doc_type=filetype, id=filename, 
            body={
            "full-chains":full_chains,
            "short-chains": short_chains,
            "residue-set":v})
    #except:
    #    print("Failed :(")
    os.remove(temp_name)
    return 0

def parse_chain(chain):
    residues = [{"name":r.name, "index":r.index} for r in chain.residues]
    return residues

def short_name(chain):
    result = ""
    for r in chain.residues:
        c = _AMINO_ACID_CODES.get(r.name, None)
        if r is not None and c is not None:
            result += c
    return result

def full_chain(chain):
    full_chains = "-".join([r.name for r in chain.residues])
    return full_chains

def all_residues(chain):
    return set([r.name for r in chain.residues])

def start_reindex(filename):
    job = q.enqueue(reindex_file, filename)
    return job.id
    
