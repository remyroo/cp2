import unittest
from flask import json
from tests.test_base import BaseTestCase
from bucketlist.models import BucketlistItem


class TestBucketlistItemViews(BaseTestCase):
    """
    Test bucketlist item interactions.
    """
    def test_item_access_with_invalid_token(self):
        """Tests unauthorized error raised with invalid token."""
        response = self.client.post("/bucketlists/1/items/",
                                    data=json.dumps(dict(name="item",
                                                         done="")),
                                    content_type="application/json",
                                    headers={"Authorization": "Token " + "invalid"})
        self.assertEqual(response.status_code, 401)

    def test_add_new_item(self):
        """Tests a new item can be added."""
        response = self.client.post("/bucketlists/1/items/",
                                    data=json.dumps(dict(name="testbucketitem",
                                                         done="")),
                                    content_type="application/json",
                                    headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 201)
        response_msg = json.loads(response.data)
        self.assertIn("Testbucketitem", response_msg["Message"])

        # asserts that the bucketlist item is assigned to the correct bucketlist
        item = BucketlistItem.query.filter_by(name="testbucketitem").first()
        self.assertEqual(item.bucket, 1)

    def test_bucketlist_validation_for_new_item(self):
        """
        Tests error raised if bucketlist doesn't exist
        before creating a new item.
        """
        response = self.client.post("/bucketlists/3/items/",
                                    data=json.dumps(dict(name="testbucketitem",
                                                         done="")),
                                    content_type="application/json",
                                    headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 404)
        response_msg = json.loads(response.data)
        self.assertIn("bucketlist was not found", response_msg["Message"])

    def test_invalid_name(self):
        """Tests error raised when empty string passed."""
        response = self.client.post("/bucketlists/1/items/",
                                    data=json.dumps(dict(name="",
                                                         done="yes")),
                                    content_type="application/json",
                                    headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 400)
        response_msg = json.loads(response.data)
        self.assertIn("must have a name", response_msg["Message"])

    def test_done_defaults_to_false(self):
        """
        Tests for new items, when the done field is
        an empty string, it defaults to False in the db.
        """
        response = self.client.post("/bucketlists/1/items/",
                                    data=json.dumps(dict(name="new item",
                                                         done="")),
                                    content_type="application/json",
                                    headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 201)

        # asserts that the value of the done field is False in the db
        new_item = BucketlistItem.query.filter_by(name="new item").first()
        self.assertEqual(new_item.done, False)

    def test_item_duplicates_prevented(self):
        """
        Tests error is raised for item duplicates.

        An item named 'testitem' was already created in setUp.
        """
        response = self.client.post("/bucketlists/1/items/",
                                    data=json.dumps(dict(name="testitem",
                                                         done="yes")),
                                    content_type="application/json",
                                    headers={"Authorization": "Token " + self.token})
        self.assertEqual(response.status_code, 400)
        response_msg = json.loads(response.data)
        self.assertIn("already exists", response_msg["Message"])

    def test_invalid_update_request(self):
        """Tests error raised when requested item doesn't exist."""
        response = self.client.put("/bucketlists/1/items/2",
                                   data=json.dumps(dict(name="updated_name")),
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 404)
        response_msg = json.loads(response.data)
        self.assertIn("not found", response_msg["Message"])

    def test_update_name_field(self):
        """Tests an item's name can be updated."""
        response = self.client.put("/bucketlists/1/items/1",
                                   data=json.dumps(dict(name="updated_name")),
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("Updated_Name", response_msg["Message"])

    def test_invalid_name_update(self):
        """Tests name is not changed even if empty string is passed."""
        response = self.client.put("/bucketlists/1/items/1",
                                   data=json.dumps(dict(name="")),
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("Testitem", response_msg["Message"])

    def test_update_item_done_field(self):
        """Tests an item's done field can be updated."""
        response = self.client.put("/bucketlists/1/items/1",
                                   data=json.dumps(dict(done="yes")),
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)

        # asserts that the item in the db has actually been updated
        updated_item = BucketlistItem.query.filter_by(id=1).first()
        self.assertEqual(updated_item.done, True)

    def test_invalid_done_update(self):
        """Tests done is not changed even if empty string is passed."""
        response = self.client.put("/bucketlists/1/items/1",
                                   data=json.dumps(dict(done="")),
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)

        # asserts that the item's done field in the db has not been changed
        updated_item = BucketlistItem.query.filter_by(id=1).first()
        self.assertEqual(updated_item.done, False)

    def test_delete_item(self):
        """Tests an item can be deleted."""
        response = self.client.delete("/bucketlists/1/items/1",
                                      content_type="application/json",
                                      headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("deleted", response_msg["Message"])

        # asserts that the item has been deleted from the db
        self.assertEqual(BucketlistItem.query.get(1), None)

    def test_invalid_delete(self):
        """Tests error raised for an invalid delete request."""
        response = self.client.delete("/bucketlists/1/items/2",
                                      content_type="application/json",
                                      headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 404)
        response_msg = json.loads(response.data)
        self.assertIn("not found", response_msg["Message"])


if __name__ == '__main__':
    unittest.main()
