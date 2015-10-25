from flask import Flask, render_template
from elasticsearch import Elasticsearch
from rq import Queue
from redis import Redis
import boto
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.security import Security, SQLAlchemyUserDatastore
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)


mail = Mail(app)
db = SQLAlchemy(app)
es = Elasticsearch()

redis = Redis()
q = Queue(connection=redis)

if app.config.get("S3_SECRET", None) is not None:
    s3 = boto.connect_s3(app.config["S3_SECRET"], app.config["S3_KEY"])
    bucket = s3.get_bucket(app.config["S3_BUCKET"])
else:
    bucket = None

import modules.hello
#import modules.indexing
import modules.login
import modules.upload
import modules.simulations
from modules.login import User, Role

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.route("/")
def index():
    return render_template("index.html")
