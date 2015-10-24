from modules import app, q, es, bucket
from flask import abort, request
import mdtraj as md
import boto
import uuid
import os

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
    full_chains = [[full_chain(c)] for c in traj.topology.chains]
    residue_set = [all_residues(c) for c in traj.topology.chains]
    v = []
    for s in residue_set:
        v += list(s)
    es.index(index="mddb-index", doc_type=filetype, id=filename, 
            body={
            "full-chains":full_chains,
            "residue-set":v})
    #except:
    #    print("Failed :(")
    os.remove(temp_name)
    return 0

def parse_chain(chain):
    residues = [{"name":r.name, "index":r.index} for r in chain.residues]
    return residues

def full_chain(chain):
    full_chains = "-".join([r.name for r in chain.residues])
    return full_chains

def all_residues(chain):
    return set([r.name for r in chain.residues])

def start_reindex(filename):
    job = q.enqueue(reindex_file, filename)
    return job.id
    
