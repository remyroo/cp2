from datetime import datetime
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from bucketlist import db


class ValidationError(ValueError):
    pass


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, index=True)
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
            if not data["username"] or not data["password"]:
                return "Missing"
            else:
                self.username = data["username"]
                self.password_hash = data["password"]
        except KeyError as e:
            raise ValidationError("Missing field: " + e.args[0])
        return self


class Bucketlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(100), index=True)
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_modified = db.Column(db.DateTime, default=datetime.now,
                              onupdate=datetime.now)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    items = db.relationship("BucketlistItem", backref="bucketlist",
                            lazy="dynamic", cascade="all, delete-orphan")

    def export_data(self):
        return {
            "id": self.id,
            "list_name": self.list_name,
            "items": [{
                "id": item.id,
                "name": item.name,
                "date_created": item.date_created,
                "date_modified": item.date_modified,
                "done": item.done} for item in self.items],
            "date_created": self.date_created.isoformat(),
            "date_modified": self.date_modified.isoformat(),
            "created_by": self.created_by
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
    date_modified = db.Column(db.DateTime, default=datetime.now,
                              onupdate=datetime.now)
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
