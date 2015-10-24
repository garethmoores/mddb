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
    temp_name = "/tmp/mmdb/" + uuid.uuid4()
    key.key = filename
    key.get_contents_to_filename(temp_name)
    traj = md.load(temp_name)
    es.index(index="mddb-index", doc_type=filetype, id=filetype[0], 
            body={"residues": traj.topology.residues})
    os.remove(temp_name)
    return 0

def start_reindex(filename):
    job = q.enqueue(reindex_file, filename)
    return job.id
    
