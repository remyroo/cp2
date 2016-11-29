import unittest
from flask import json
from tests.test_base import BaseTestCase
from bucketlist.models import BucketlistItem


class TestBucketlistItemViews(BaseTestCase):
    """
    Test bucketlist item interactions
    """
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

    def test_update_item_name(self):
        """Tests an item's name can be updated."""
        response = self.client.put("/bucketlists/1/items/1",
                                   data=json.dumps(dict(name="updated_name")),
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("Updated_Name", response_msg["Message"])

    def test_update_item_done(self):
        """Tests an item's done field can be updated."""
        response = self.client.put("/bucketlists/1/items/1",
                                   data=json.dumps(dict(done="yes")),
                                   content_type="application/json",
                                   headers={'Authorization': 'Token ' + self.token})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("Updated", response_msg["Message"])

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


if __name__ == '__main__':
    unittest.main()
