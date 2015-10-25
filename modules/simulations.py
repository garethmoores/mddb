from modules import app, db
from flask import abort, request, render_template, redirect
from datetime import datetime
from flask.ext.security import current_user


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
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner_relationship = db.relationship('User', 
            backref=db.backref('simulations', lazy='dynamic'))
    
    parent = db.Column(db.Integer, nullable=True,
            db.ForeignKey('simulation.id'))
    parent_relationship = db.relationship('Simulation',
            backref=db.backref('child', lazy='dynamic'))

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
        self.date = datettime.utcnow()
        self.owner = owner.id
        self.title = title
        self.engine = engine
        self.force_field = force_field
        self.protein = protein
        if parent is not None:
            self.parent = parent


@app.route('/simulation/new/', method=['POST'])
def new_sim():
    owner = current_user()
    title = request.form.get('title', None)
    engine = request.form.get('engine', None)
    force_field = request.form.get('force_field', None)
    protein = request.form.get('protein', None)
    if title is None or engine is None or force_field is None or protein is None:
        abort(401)
    sim = Simulation(owner=owner.id, title=title, engine=engine, 
            force_field=firce_field, protein=protein)
    db.session.add(sim)
    db.session.commit()
    return redirect('/simulations/' + str(sim.id))


@app.route('/simulations/<sim_id>', methods=['GET', 'POST'])
def get_sim(sim_id):
    sim = Simulation.query.filter_by(id=sim_id).first()
    if sim is None:
        abort(404)
    return render_template('simulation.html', sim=sim)


