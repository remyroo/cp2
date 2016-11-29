import unittest
from flask import json
from tests.test_base import BaseTestCase
from bucketlist.models import Bucketlist


class TestBucketlistViews(BaseTestCase):
    """
    Test bucketlist interactions.
    """
    def test_add_new_bucketlist(self):
        """Tests a new bucketlist can be added."""
        response = self.client.post("/bucketlists/",
                                    data=json.dumps(dict(name="bucketlist")),
                                    content_type="application/json",
                                    headers={"Authorization": "Token " + self.token})
        self.assertEqual(response.status_code, 201)
        response_msg = json.loads(response.data)
        self.assertIn("Bucketlist", response_msg["Message"])

    def test_duplicates_prevented(self):
        """
        Tests a new bucketlist can be added.
        
        A bucket named 'testbucketlist' was already created in setUp
        """
        response = self.client.post("/bucketlists/",
                                    data=json.dumps(dict(name="testbucketlist")),
                                    content_type="application/json",
                                    headers={"Authorization": "Token " + self.token})
        self.assertEqual(response.status_code, 400)
        response_msg = json.loads(response.data)
        self.assertIn("already exists", response_msg["Message"])

    def test_return_all_bucketlists(self):
        """Tests retrieval of all bucketlists."""
        response = self.client.get("/bucketlists/",
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        response_msg = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_msg["Bucketlists"]), 2)

    def test_get_bucketlist(self):
        """
        Tests retrieval of a single bucketlist.

        Two test bucketlist items were added in the setUp to
        test that the id parameter works correctly.
        """
        response = self.client.get("/bucketlists/2",
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("testbucketlist2", response_msg["Bucketlist"]["name"])

    def test_update_bucketlist(self):
        """Tests a bucketlist can be updated."""
        response = self.client.put("/bucketlists/2",
                                   data=json.dumps(dict(name="updated_name")),
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("Updated_Name", response_msg["Message"])

    def test_delete_bucketlist(self):
        """Tests bucketlist deletion."""
        response = self.client.delete("/bucketlists/1",
                                      content_type="application/json",
                                      headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)

        # asserts that the bucketlist has been deleted from the db
        self.assertEqual(Bucketlist.query.get(1), None)

    def test_pagination(self):
        """Tests specified number of results retrieved from GET request."""
        response = self.client.get("/bucketlists/?limit=2",
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertEqual(2, response_msg["count"])

    def test_search_by_bucketlist_name(self):
        """Tests bucketlist can be retrieved from search."""
        response = self.client.get("/bucketlists/?q=testbucketlist",
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertEqual("testbucketlist", response_msg["Bucketlists"][0]["name"])


if __name__ == '__main__':
    unittest.main()
