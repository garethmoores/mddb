from modules import app, q, es
from flask import abort, request

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
    es.index(index="mddb-index", doc_type=filetype, id=filetype[0], 
            body={"Hello": "world"})
    return 0

def start_reindex(filename):
    job = q.enqueue(reindex_file, filename)
    return job.id
    
