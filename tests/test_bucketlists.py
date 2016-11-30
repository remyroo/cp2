import unittest
from flask import json
from tests.test_base import BaseTestCase
from bucketlist.models import Bucketlist


class TestBucketlistViews(BaseTestCase):
    """
    Test bucketlist interactions.
    """
    def test_bucketlist_access_with_invalid_token(self):
        """Tests unauthorized error raised with invalid token."""
        response = self.client.post("/bucketlists/",
                                    data=json.dumps(dict(name="bucketlist")),
                                    content_type="application/json",
                                    headers={"Authorization": "Token " + "invalid"})
        self.assertEqual(response.status_code, 401)

    def test_add_new_bucketlist(self):
        """Tests a new bucketlist can be added."""
        response = self.client.post("/bucketlists/",
                                    data=json.dumps(dict(name="bucketlist")),
                                    content_type="application/json",
                                    headers={"Authorization": "Token " + self.token})
        self.assertEqual(response.status_code, 201)
        response_msg = json.loads(response.data)
        self.assertIn("Bucketlist", response_msg["Message"])

    def test_invalid_name(self):
        """Tests error raised when empty string passed."""
        response = self.client.post("/bucketlists/",
                                    data=json.dumps(dict(name="")),
                                    content_type="application/json",
                                    headers={"Authorization": "Token " + self.token})
        self.assertEqual(response.status_code, 400)
        response_msg = json.loads(response.data)
        self.assertIn("must have a name", response_msg["Message"])

    def test_duplicates_prevented(self):
        """
        Tests error is raised for duplicates.
        
        A bucket named 'testbucketlist' was already created in setUp.
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

        Two test bucketlists were added in the setUp to
        test that the id parameter works correctly.
        """
        response = self.client.get("/bucketlists/2",
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("Testbucketlist2", response_msg["Bucketlist"]["name"])

    def test_bucketlist_access_by_user(self):
        """
        Tests user cannot access bucketlists owned by another user.
        
        A 3rd test bucketlist was created by a different user 
        in setUp to test that user access works correctly.
        """
        response = self.client.get("/bucketlists/3",
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 404)
        response_msg = json.loads(response.data)
        self.assertIn("not found", response_msg["Message"])

    def test_invalid_bucketlist_get_request(self):
        """Tests error raised for an invalid get request."""
        response = self.client.get("/bucketlists/3",
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 404)
        response_msg = json.loads(response.data)
        self.assertIn("not found", response_msg["Message"])

    def test_update_bucketlist(self):
        """Tests a bucketlist can be updated."""
        response = self.client.put("/bucketlists/2",
                                   data=json.dumps(dict(name="updated_name")),
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("Updated_Name", response_msg["Message"])

    def test_invalid_update(self):
        """Tests error raised for an invalid update request."""
        response = self.client.put("/bucketlists/3",
                                   data=json.dumps(dict(name="updated_name")),
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 404)
        response_msg = json.loads(response.data)
        self.assertIn("not found", response_msg["Message"])

    def test_delete_bucketlist(self):
        """Tests bucketlist deletion."""
        response = self.client.delete("/bucketlists/1",
                                      content_type="application/json",
                                      headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("deleted", response_msg["Message"])

        # asserts that the bucketlist has been deleted from the db
        self.assertEqual(Bucketlist.query.get(1), None)

    def test_invalid_delete(self):
        """Tests error raised for an invalid delete request."""
        response = self.client.delete("/bucketlists/3",
                                      content_type="application/json",
                                      headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 404)
        response_msg = json.loads(response.data)
        self.assertIn("not found", response_msg["Message"])

    def test_results_limit(self):
        """Tests specified number of results retrieved from GET request."""
        response = self.client.get("/bucketlists/?limit=1",
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertEqual(1, response_msg["count"])

    def test_invalid_limit(self):
        """Tests error raised for non-integer limit request."""
        response = self.client.get("/bucketlists/?limit=invalid",
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 400)
        response_msg = json.loads(response.data)
        self.assertIn("use numbers", response_msg["Message"])

    def test_pagination(self):
        """Tests specified number of pages returned from GET request."""
        response = self.client.get("/bucketlists/?page=1",
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertTrue(response_msg["next"], "None")

    def test_invalid_pagination(self):
        """Tests error raised for non-integer pagination request."""
        response = self.client.get("/bucketlists/?page=invalid",
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 400)
        response_msg = json.loads(response.data)
        self.assertIn("use numbers", response_msg["Message"])

    def test_search_by_bucketlist_name(self):
        """Tests bucketlist can be retrieved from search."""
        response = self.client.get("/bucketlists/?q=Testbucketlist",
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertEqual("Testbucketlist", response_msg["Bucketlists"][0]["name"])

    def test_invalid_search(self):
        """Tests error raised for invalid search."""
        response = self.client.get("/bucketlists/?q=invalid",
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 404)
        response_msg = json.loads(response.data)
        self.assertIn("not found", response_msg["Message"])


if __name__ == '__main__':
    unittest.main()
