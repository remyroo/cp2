import os
from datetime import datetime
from flask import Flask, url_for, jsonify, request, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "../bucketlist.sqlite")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SECRET_KEY"] = "Super_Secret"

db = SQLAlchemy(app)
auth = HTTPBasicAuth()
auth_token = HTTPTokenAuth("Token")


# MODELS:
class ValidationError(ValueError):
    pass

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True)
    password_hash = db.Column(db.String(128))
    bucketlists = db.relationship("Bucketlist", backref="user", lazy="dynamic",
                                  cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def export_data(self):
        return {
            "username": self.username,
            "bucketlist_url": url_for("all_bucketlists", id=self.id, _external=True)
        }

    def import_data(self, data):
        try:
            self.username = data["username"]
            self.password_hash = data["password"]
        except KeyError as e:
            raise ValidationError("Invalid, missing: " + e.args[0])
        return self


class Bucketlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(100), index=True)
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_modified = db.Column(db.DateTime, default=datetime.now)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    items = db.relationship("BucketlistItem", backref="bucketlist",
                            lazy="dynamic", cascade="all, delete-orphan")

    def export_data(self):
        return {
            "id": self.id,
            "list_name": self.list_name,
            "date_created": self.date_created.isoformat() + "Z",
            "date_modified": self.date_modified.isoformat() + "Z",
        }

    def import_data(self, data):
        try:
            self.list_name = data["list_name"]
        except KeyError as e:
            raise ValidationError("Invalid, missing: " + e.args[0])
        return self


class BucketlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, index=True)
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_modified = db.Column(db.DateTime, default=datetime.now)
    done = db.Column(db.Boolean, default=False)
    bucket = db.Column(db.Integer, db.ForeignKey("bucketlist.id"))

    def export_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "date_created": self.date_created.isoformat() + "Z",
            "date_modified": self.date_modified.isoformat() + "Z",
            "done": self.done
        }

    def import_data(self, data):
        try:
            self.name = data["name"]
            self.done = data["done"]
        except KeyError as e:
            raise ValidationError("Invalid, missing: " + e.args[0])
        return self


# LOGIN AUTH:
@auth.verify_password
def verify_password(username, password):
    g.user = User.query.filter_by(username=username).first()
    if g.user is None:
        return False
    elif g.user.check_password(password):
        return g.user


# TOKEN AUTH:
def generate_auth_token(user_id, expires_in=3600):
    s = Serializer(app.config["SECRET_KEY"], expires_in=expires_in)
    return s.dumps({"id": g.user.id})


@auth_token.verify_token
def verify_auth_token(token):
    s = Serializer(app.config["SECRET_KEY"])
    try:
        data = s.loads(token)
    except:
        return None
    g.user = User.query.get(data["id"])
    return g.user


# VIEWS:
@app.route("/auth/register", methods=["POST"])
def new_user():
    user = User()
    user.import_data(request.json)
    user.set_password(user.password_hash)
    db.session.add(user)
    db.session.commit()
    return jsonify({"Message": user.username.title() + " has been created"}), 201


@app.route("/auth/login", methods=["POST"])
def login():
    user = User()
    user.import_data(request.json)
    username = user.username
    password = user.password_hash
    if verify_password(username, password):
        return jsonify({"Token": generate_auth_token(g.user.id)}), 200
    return jsonify({"Message": "Invalid username or password. Please try again"}), 401


@app.route("/users/<int:user_id>", methods=["PUT"])
@auth_token.login_required
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        user.import_data(request.json)
        db.session.add(user)
        db.session.commit()
        return jsonify({"Message": user.username.title() + " has been updated"}), 200
    except:
        return jsonify({"Message": "That user does not exist"}), 404

@app.route("/bucketlists/", methods=["POST"])
@auth_token.login_required
def new_bucketlist():
    bucketlist = Bucketlist()
    bucketlist.import_data(request.json)
    bucketlist.created_by = g.user.id
    db.session.add(bucketlist)
    db.session.commit()
    return jsonify({"Message": bucketlist.list_name.title() + " has been created"}), 201


@app.route("/bucketlists/", methods=["GET"])
@auth_token.login_required
def all_bucketlists():
    try:
        return jsonify({"All bucketlists": [bucketlist.export_data()
                        for bucketlist in Bucketlist.query.all()]}), 200
    except:
        return jsonify({"Message": "There are no bucketlists"}), 404


@app.route("/bucketlists/<int:bucket_id>", methods=["GET"])
@auth_token.login_required
def get_bucketlist(bucket_id):
    try:
        return jsonify({"Bucketlist": Bucketlist.query.get_or_404(bucket_id).export_data()}), 200
    except:
        return jsonify({"Message": "That bucketlist does not exist"}), 404

@app.route("/bucketlists/<int:bucket_id>", methods=["PUT"])
@auth_token.login_required
def update_bucketlist(bucket_id):
    try:
        bucketlist = Bucketlist.query.get_or_404(bucket_id)
        bucketlist.import_data(request.json)
        db.session.add(bucketlist)
        db.session.commit()
        return jsonify({"Message": bucketlist.list_name.title() + " has been updated"}), 200
    except:
        return jsonify({"Message": "That bucketlist does not exist"}), 404


@app.route("/bucketlists/<int:bucket_id>", methods=["DELETE"])
@auth_token.login_required
def delete_bucketlist(bucket_id):
    try:
        bucketlist = Bucketlist.query.get_or_404(bucket_id)
        db.session.delete(bucketlist)
        db.session.commit()
        return jsonify({"Message": bucketlist.list_name.title() + " has been deleted"}), 200
    except:
        return jsonify({"Message": "That bucketlist does not exist"}), 404

@app.route("/bucketlists/<int:bucket_id>/items", methods=["POST"])
@auth_token.login_required
def new_item(bucket_id):
    Bucketlist.query.get_or_404(bucket_id)
    item = BucketlistItem()
    item.bucket = bucket_id
    item.import_data(request.json)
    db.session.add(item)
    db.session.commit()
    return jsonify({"Message": item.name.title() + " item has been created"}), 201


@app.route("/bucketlists/<int:bucket_id>/items/<int:item_id>", methods=["PUT"])
@auth_token.login_required
def update_item(bucket_id, item_id):
    itemlist = BucketlistItem.query.filter_by(bucket=bucket_id)
    for item in itemlist:
        if item.id == item_id:
            item.import_data(request.json)
            db.session.add(item)
            db.session.commit()
            return jsonify({"Message": item.name.title() + " has been updated"}), 200
        return jsonify({"Message": "Item does not exist"}), 404


@app.route("/bucketlists/<int:bucket_id>/items/<int:item_id>", methods=["DELETE"])
@auth_token.login_required
def delete_item(bucket_id, item_id):
    itemlist = BucketlistItem.query.filter_by(bucket=bucket_id)
    for item in itemlist:
        if item.id == item_id:
            item.import_data(request.json)
            db.session.delete(item)
            db.session.commit()
            return jsonify({"Message": item.name.title() + "has been deleted"}), 200
        return jsonify({"Message": "Item does not exist"}), 404


if __name__ == '__main__':
    db.create_all()
    app.run()

