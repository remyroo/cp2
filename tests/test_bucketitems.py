import unittest
from flask import json
from tests.test_base import BaseTestCase
from bucketlist.models import BucketlistItem


class TestBucketlistItemViews(BaseTestCase):
    '''
    Test bucketlist item interactions
    '''
    def test_add_new_item(self):
        response = self.client.post("/auth/login",
                                    data=json.dumps(dict(username="testuser",
                                                    password="testpass")),
                                    content_type="application/json")
        response_msg = json.loads(response.data)
        token = response_msg["Token"]

        response = self.client.post("/bucketlists/1/items",
                                    data=json.dumps(dict(name="testbucketitem", done="")),
                                    content_type="application/json",
                                    headers={'Authorization': 'Token ' + token})
        self.assertEqual(response.status_code, 201)
        response_msg = json.loads(response.data)
        self.assertIn("Testbucketitem", response_msg["Message"])

        '''Asserts that the bucketlist item is assigned to the correct bucketlist'''
        item = BucketlistItem.query.filter_by(name="testbucketitem").first()
        self.assertEqual(item.bucket, 1)

    def test_update_item(self):
        response = self.client.post("/auth/login",
                                    data=json.dumps(dict(username="testuser",
                                                    password="testpass")),
                                    content_type="application/json")
        response_msg = json.loads(response.data)
        token = response_msg["Token"]

        response = self.client.put("/bucketlists/1/items/1",
                                   data=json.dumps(dict(name="updated_name", done="True")),
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("Updated_Name", response_msg["Message"])

    def test_delete_item(self):
        response = self.client.post("/auth/login",
                                    data=json.dumps(dict(username="testuser",
                                                    password="testpass")),
                                    content_type="application/json")
        response_msg = json.loads(response.data)
        token = response_msg["Token"]

        response = self.client.delete("/bucketlists/1/items/1",
                                      content_type="application/json",
                                      headers={'Authorization': 'Token ' + token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)

        '''Asserts that the item has been deleted from the db'''
        self.assertEqual(BucketlistItem.query.get(1), None)


if __name__ == '__main__':
    unittest.main()
