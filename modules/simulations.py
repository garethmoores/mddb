from modules import app, db, bucket, q, es
from modules.indexing import reindex_and_delete
from modules.login import User
from flask import abort, request, render_template, redirect
from datetime import datetime
from flask.ext.security import current_user
from werkzeug import secure_filename
import boto
import os
import uuid

class SimFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    simulation = db.Column(db.Integer, db.ForeignKey('simulation.id'))
    simulation_relationship = db.relationship('Simulation', 
            backref=db.backref('files', lazy='dynamic'))

    def __init__(self, filename, simulation):
        self.filename = filename
        self.simulation = simulation.id

# class comments

class Simulation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner_relationship = db.relationship('User', 
            backref=db.backref('simulations', lazy='dynamic'))
    
    parent = db.Column(db.Integer,
            db.ForeignKey('simulation.id'), nullable=True)

    # protein name *
    protein = db.Column(db.String(500))
    # force field *
    force_field = db.Column(db.String(500))
    # engine *
    engine = db.Column(db.String(255))
    # title *
    title = db.Column(db.String(255), unique=True)
    # date *
    date = db.Column(db.DateTime)

    def __init__(self, owner, title, engine, force_field, protein, parent=None):
        self.date = datetime.utcnow()
        self.owner = owner
        self.title = title
        self.engine = engine
        self.force_field = force_field
        self.protein = protein
        if parent is not None:
            self.parent = parent

Simulation.parent_relationship = db.relationship('Simulation',
            backref=db.backref('child', lazy='dynamic'), remote_side=Simulation.id)


@app.route('/simulations/new/', methods=['GET', 'POST'])
def new_sim():
    if request.method == 'POST':
        owner = current_user
        title = request.form.get('title', None)
        engine = request.form.get('engine', None)
        force_field = request.form.get('force_field', None)
        protein = request.form.get('protein', None)
        if title is None or engine is None or force_field is None or protein is None:
            abort(401)
        sim = Simulation(owner=owner.id, title=title, engine=engine, 
                force_field=force_field, protein=protein)
        db.session.add(sim)
        db.session.commit()
        es.index(index="mddb-index", doc_type="simulation",
                id=sim.id, body={
                    "title": title,
                    "engine": engine,
                    "force_field": force_field,
                    "protein": protein
                    })
        return redirect('/simulations/view/' + str(sim.id))
    else:
        return render_template('simulation_form.html')


@app.route('/simulations/view/<sim_id>', methods=['GET', 'POST'])
def get_sim(sim_id):
    sim = Simulation.query.filter_by(id=sim_id).first()
    if sim is None:
        abort(404)
    owner = User.query.filter_by(id=sim.owner).first()
    return render_template('simulation.html', sim=sim, user=owner)

@app.route('/simulations/addfile/<sim_id>', methods=['POST'])
def upload_file(sim_id):
    sim = Simulation.query.filter_by(id=sim_id).first()
    if sim is None:
        about(404)
    uploaded = request.files['file']
    filename = str(uuid.uuid4()) +"-"+ secure_filename(uploaded.filename)
    uploaded.save(os.path.join('/tmp/mddb/', filename))
    q.enqueue(to_s3_and_reindex, sim_id, uploaded.filename, filename)
    file_object = SimFile(filename=os.path.join('/simulations/' + str(sim_id),
        uploaded.filename), simulation=sim)
    db.session.add(file_object)
    db.session.commit()
    return redirect('/simulations/view/' + str(sim_id))

def to_s3_and_reindex(id, filename, local):
    # do some s3 magic + index
    key = boto.s3.key.Key(bucket)
    key.key = os.path.join('/simulations/' + str(id), 
            secure_filename(filename))
    key.set_contents_from_filename(os.path.join('/tmp/mddb/', local))
    reindex_and_delete(local)
