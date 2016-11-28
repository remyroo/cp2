from datetime import datetime
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from bucketlist import db
from bucketlist.exceptions import ValidationError


class User(db.Model):
    """
    Models the User class
    """
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
            if len(data["username"].strip()) == 0 or len(data["password"].strip()) == 0:
                return "Invalid"
            else:
                self.username = data["username"]
                self.password_hash = data["password"]
        except KeyError as e:
            raise ValidationError("Missing field: " + e.args[0])
        return self


class Bucketlist(db.Model):
    """
    Models the bucketlist class
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_modified = db.Column(db.DateTime, default=datetime.now,
                              onupdate=datetime.now)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    items = db.relationship("BucketlistItem", backref="bucketlist",
                            lazy="dynamic", cascade="all, delete-orphan")

    def export_data(self):
        return {
            "id": self.id,
            "name": self.name,
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
            if len(data["name"].strip()) == 0:
                return "Invalid"
            else:
                self.name = data["name"]
        except KeyError as e:
            raise ValidationError("Invalid, missing: " + e.args[0])
        return self

    def update_data(self, data):
        self.name = data.get("name", self.name)
        return self


class BucketlistItem(db.Model):
    """
    Models the item class
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, index=True)
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_modified = db.Column(db.DateTime, default=datetime.now,
                              onupdate=datetime.now)
    done = db.Column(db.Boolean, default=False)
    bucket = db.Column(db.Integer, db.ForeignKey("bucketlist.id"))
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"))

    def export_data(self):
        return url_for("all_bucketlists", id=self.id, _external=True)

    def import_data(self, data):
        try:
            if len(data["name"].strip()) == 0:
                return "Invalid"
            else:
                self.name = data["name"]
            if data["done"].strip() == "yes":
                self.done = True
            else:
                self.done = False
        except KeyError as e:
            raise ValidationError("Invalid, missing: " + e.args[0])
        return self

    def update_data(self, data):
        self.name = data.get("name", self.name)
        self.done = data.get("done", self.done)
        return self
