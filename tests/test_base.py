import unittest
from flask import json
from manage import app, db
from bucketlist.models import Bucketlist, BucketlistItem
from config import TestingConfig


class BaseTestCase(unittest.TestCase):
    """
    A base test case which creates dummy
    user, bucketlist and bucketlist item db entries.
    """
    def setUp(self):
        """
        Add bucketlists and items directly to db to avoid using tokens 
        required for POST request.
        """
        app.config.from_object(TestingConfig)
        self.client = app.test_client()
        db.create_all()

        self.client.post("/auth/register",
                         data=json.dumps(dict(username="testuser",
                                              password="testpass")),
                         content_type="application/json")

        response = self.client.post("/auth/login",
                                    data=json.dumps(dict(username="testuser",
                                                    password="testpass")),
                                    content_type="application/json")
        response_msg = json.loads(response.data)
        self.token = response_msg["Token"]

        bucket = {"name": "testbucketlist"}
        test_bucket = Bucketlist()
        test_bucket.import_data(bucket)
        test_bucket.created_by = 1

        bucket2 = {"name": "testbucketlist2"}
        test_bucket2 = Bucketlist()
        test_bucket2.import_data(bucket2)
        test_bucket2.created_by = 1

        bucket3 = {"name": "testbucketlist3"}
        test_bucket3 = Bucketlist()
        test_bucket3.import_data(bucket3)
        test_bucket3.created_by = 2

        item = {"name": "testitem", "done": ""}
        test_item = BucketlistItem()
        test_item.import_data(item)
        test_item.bucket = 1
        test_item.created_by = 1

        db.session.add(test_bucket)
        db.session.add(test_bucket2)
        db.session.add(test_bucket3)
        db.session.add(test_item)
        db.session.commit()

    def tearDown(self):
        """Drops the db."""
        db.session.remove()
        db.drop_all()
