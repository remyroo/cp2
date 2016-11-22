import unittest
from flask import json
from tests.test_base import BaseTestCase
from bucketlist.models import Bucketlist


class TestBucketlistViews(BaseTestCase):
    '''
    Test bucketlist interactions. These views
    require a token to access them 
    '''
    def test_add_new_bucketlist(self):
        response = self.client.post("/auth/login",
                                    data=json.dumps(dict(username="testuser",
                                                    password="testpass")),
                                    content_type="application/json")
        response_msg = json.loads(response.data)
        token = response_msg["Token"]

        response = self.client.post("/bucketlists/",
                                    data=json.dumps(dict(list_name="testbucketlist")),
                                    content_type="application/json",
                                    headers={"Authorization": "Token " + token})
        self.assertEqual(response.status_code, 201)
        response_msg = json.loads(response.data)
        self.assertIn("Testbucketlist", response_msg["Message"])

    def test_return_all_bucketlists(self):
        response = self.client.post("/auth/login",
                                    data=json.dumps(dict(username="testuser",
                                                    password="testpass")),
                                    content_type="application/json")
        response_msg = json.loads(response.data)
        token = response_msg["Token"]

        response = self.client.get("/bucketlists/",
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + token})
        response_msg = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_msg["Bucketlists"]), 2)

    def test_get_bucketlist(self):
        '''
        Two test bucketlist items were added in the setUp to test
        the GET bucketlist id request works correctly
        '''
        response = self.client.post("/auth/login",
                                    data=json.dumps(dict(username="testuser",
                                                    password="testpass")),
                                    content_type="application/json")
        response_msg = json.loads(response.data)
        token = response_msg["Token"]

        response = self.client.get("/bucketlists/2",
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("testbucketlist2", response_msg["Bucketlist"]["list_name"])

    def test_update_bucketlist(self):
        response = self.client.post("/auth/login",
                                    data=json.dumps(dict(username="testuser",
                                                    password="testpass")),
                                    content_type="application/json")
        response_msg = json.loads(response.data)
        token = response_msg["Token"]

        response = self.client.put("/bucketlists/2",
                                   data=json.dumps(dict(list_name="updated_name")),
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("Updated_Name", response_msg["Message"])

    def test_delete_bucketlist(self):
        response = self.client.post("/auth/login",
                                    data=json.dumps(dict(username="testuser",
                                                    password="testpass")),
                                    content_type="application/json")
        response_msg = json.loads(response.data)
        token = response_msg["Token"]

        response = self.client.delete("/bucketlists/1",
                                      content_type="application/json",
                                      headers={'Authorization': 'Token ' + token})
        self.assertEqual(response.status_code, 200)

        '''Asserts that the bucketlist has been deleted from the db'''
        self.assertEqual(Bucketlist.query.get(1), None)

    def test_pagination(self):
        response = self.client.post("/auth/login",
                                    data=json.dumps(dict(username="testuser",
                                                    password="testpass")),
                                    content_type="application/json")
        response_msg = json.loads(response.data)
        token = response_msg["Token"]

        response = self.client.get("/bucketlists/?limit=2",
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertEqual(2, response_msg["count"])

    def test_search_by_bucketlist_name(self):
        response = self.client.post("/auth/login",
                                    data=json.dumps(dict(username="testuser",
                                                    password="testpass")),
                                    content_type="application/json")
        response_msg = json.loads(response.data)
        token = response_msg["Token"]

        response = self.client.get("/bucketlists/?q=testbucketlist",
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertEqual("testbucketlist", response_msg["Bucketlists"][0]["list_name"])


if __name__ == '__main__':
    unittest.main()
