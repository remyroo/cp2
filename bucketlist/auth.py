from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import g
from bucketlist import app
from bucketlist.models import User


auth = HTTPBasicAuth()
auth_token = HTTPTokenAuth("Token")


"""Login verification"""
def verify_password(username, password):
    g.user = User.query.filter_by(username=username).first()
    if g.user is None:
        return False
    elif g.user.check_password(password):
        return g.user


"""Token generation"""
def generate_auth_token(user_id, expires_in=3600):
    s = Serializer(app.config["SECRET_KEY"], expires_in=expires_in)
    return s.dumps({"id": g.user.id})


"""Token authentication"""
@auth_token.verify_token
def verify_auth_token(token):
    s = Serializer(app.config["SECRET_KEY"])
    try:
        data = s.loads(token)
    except:
        return None
    g.user = User.query.get(data["id"])
    return g.user
