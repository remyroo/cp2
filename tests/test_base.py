import unittest
from flask import json
from manage import app, db
from bucketlist.models import Bucketlist, BucketlistItem
from config import TestingConfig


class BaseTestCase(unittest.TestCase):
    '''
    A base test case which creates dummy 
    user, bucketlist and bucketlist item db entries
    '''
    def setUp(self):
        app.config.from_object(TestingConfig)
        self.client = app.test_client()
        db.create_all()

        self.client.post("/auth/register",
                         data=json.dumps(dict(username="testuser",
                                            password="testpass")),
                         content_type="application/json")
        '''
        Add bucketlists and items directly to db to avoid using tokens 
        required for POST request
        '''
        bucket = {"list_name": "testbucketlist"}
        test_bucket = Bucketlist()
        test_bucket.import_data(bucket)
        test_bucket.created_by = 1

        bucket2 = {"list_name": "testbucketlist2"}
        test_bucket2 = Bucketlist()
        test_bucket2.import_data(bucket2)
        test_bucket2.created_by = 1

        item = {"name": "testitem", "done": ""}
        test_item = BucketlistItem()
        test_item.import_data(item)
        test_item.bucket = 1

        db.session.add(test_bucket)
        db.session.add(test_bucket2)
        db.session.add(test_item)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
