from flask import Flask, render_template
from elasticsearch import Elasticsearch
from rq import Queue
from redis import Redis
import boto
import os
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.security import Security, SQLAlchemyUserDatastore

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECRET_KEY'] = 'randomsecrety1234'

mail = Mail(app)
db = SQLAlchemy(app)
es = Elasticsearch()

redis = Redis()
q = Queue(connection=redis)

ACCESS = os.environ['ACCESS']
KEY = os.environ['KEY']

s3 = boto.connect_s3(ACCESS, KEY)
bucket = s3.get_bucket('healthhack-mddb')

import modules.hello
#import modules.indexing
import modules.login

user_datastore = SQLAlchemyUserDatastore(db, login.User, login.Role)
security = Security(app, user_datastore)

@app.route("/")
def index():
  return render_template("index.html")
