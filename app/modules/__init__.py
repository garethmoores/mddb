from flask import Flask
from elasticsearch import Elasticsearch
from rq import Queue
from redis import Redis

app = Flask(__name__)

es = Elasticsearch()

redis = Redis()
q = Queue(connection=redis)

import modules.hello
import modules.indexing

if __name__ == "__main__":
	app.run()
