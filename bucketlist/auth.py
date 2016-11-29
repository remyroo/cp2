from flask import g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from bucketlist import app
from bucketlist.models import User


auth = HTTPBasicAuth()
auth_token = HTTPTokenAuth("Token")


def verify_password(username, password):
    """
    Login verification
    """
    g.user = User.query.filter_by(username=username).first()
    if not g.user:
        return False
    elif g.user.check_password(password):
        return g.user


def generate_auth_token(user_id, expires_in=3600):
    """
    Generates a token using the user's ID
    """
    signature = Serializer(app.config["SECRET_KEY"], expires_in=expires_in)
    return signature.dumps({"id": g.user.id})


@auth_token.verify_token
def verify_auth_token(token):
    """
    Decrypts the token to verify the user's ID
    """
    signature = Serializer(app.config["SECRET_KEY"])
    try:
        data = signature.loads(token)
    except:
        return None
    g.user = User.query.get(data["id"])
    return g.user
