from flask import Flask
from elasticsearch import Elasticsearch
from rq import Queue
from redis import Redis
import boto
import os

app = Flask(__name__)

es = Elasticsearch()

redis = Redis()
q = Queue(connection=redis)

ACCESS = os.environ['ACCESS']
KEY = os.environ['KEY']

s3 = boto.connect_s3(ACCESS, KEY)
bucket = s3.get_bucket('healthhack-mddb')

import modules.hello
import modules.indexing

if __name__ == "__main__":
	app.run()
