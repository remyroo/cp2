import unittest
from flask import json
from manage import app, db
from bucketlist.models import User, Bucketlist, BucketlistItem
from config import TestingConfig


class BaseTest(unittest.TestCase):

    def setUp(self):
        app.config.from_object(TestingConfig)
        self.client = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
