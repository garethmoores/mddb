from modules import app
import urllib
from flask import request, render_template
from flask.ext.security import login_required
import base64
import json
import time
import hmac
import hashlib


@app.route("/upload/")
@login_required
def upload():
    return render_template('upload.html')

@app.route("/myuploads")
def myuploads():
    return render_template('myuploads.html')

@app.route("/upload/sign")
def sign_upload():
    S3_KEY = app.config.get('S3_KEY')
    S3_SECRET = app.config.get('S3_SECRET')
    S3_BUCKET = app.config.get('S3_BUCKET')

    object_name = urllib.quote_plus(request.args.get('file_name'))
    mime_type = request.args.get('file_type')

    expires = int(time.time()+60*60*24)
    amz_headers = "x-amz-acl:public-read"

    string_to_sign = "PUT\n\n%s\n%d\n%s\n/%s/%s" % (mime_type, expires, amz_headers, S3_BUCKET, object_name)
    signature = base64.encodestring(hmac.new(S3_SECRET.encode(), string_to_sign.encode('utf8'), hashlib.sha1).digest())

    url = 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, object_name)

    content = json.dumps({
        'signed_request': '%s?AWSAccessKeyId=%s&Expires=%s&Signature=%s' % (url, S3_KEY, expires, signature),
        'url': url,
    })

    return content
