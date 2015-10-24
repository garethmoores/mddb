from modules import app
from flask import abort, make_response
import jwt

@app.route("/auth/token", methods=["POST"])
def token():
    username = request.form.get("username")
    password = request.form.get("password")
    if password is None and username is None:
      abort(401)

    encoded = jwt.encode({'username': username}, 'secret', algorithm='HS256')
