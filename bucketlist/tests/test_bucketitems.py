import unittest
from flask import json
from bucketlist.api import app, db, User, Bucketlist, BucketlistItem


class TestAPIBucketItems(unittest.TestCase):
    '''
    Test bucketlist item interactions
    '''
    def login_test_user(self):
        '''First create a new user then log them in with a post request'''
        data = {"username": "testuser", "password": "testpass"}
        test_user = User()
        test_user.import_data(data)
        test_user.set_password(test_user.password_hash)
        db.session.add(test_user)
        db.session.commit()
        test_user_id = test_user.id

        response = self.client.post("/auth/login", data=json.dumps(
            dict(username="testuser", password="testpass")),
            content_type="application/json")
        response_msg = json.loads(response.data)
        token = response_msg["Token"]
        return token, test_user_id

    def create_test_bucketlist(self):
        data = {"list_name": "testbucketlist"}
        test_bucket = Bucketlist()
        test_bucket.import_data(data)
        test_bucket.created_by = self.login_test_user()[1]
        db.session.add(test_bucket)
        db.session.commit()
        return test_bucket.id

    def create_test_bucket_items(self):
        data = {"name": "testitem", "done": ""}
        test_item = BucketlistItem()
        test_item.import_data(data)
        test_item.bucket = self.create_test_bucketlist()

        data2 = {"name": "testitem2", "done": "True"}
        test_item2 = BucketlistItem()
        test_item2.import_data(data2)
        test_item2.bucket = test_item.bucket

        db.session.add(test_item)
        db.session.add(test_item2)
        db.session.commit()
        return test_item, test_item2

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tests/test.sqlite"
        app.config["TESTING"] = True
        self.client = app.test_client()
        db.create_all()
        self.create_test_bucket_items()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_add_new_item(self):
        response = self.client.post("/bucketlists/1/items",
                                    data=json.dumps(dict(name="testbucketitem", done="")), content_type="application/json",
                                    headers={'Authorization': 'Token ' + self.login_test_user()[0]})
        self.assertEqual(response.status_code, 201)
        response_msg = json.loads(response.data)
        self.assertIn("Testbucketitem", response_msg["Message"])
        '''Asserts that the bucketlist item is assigned to the correct bucketlist'''
        item = BucketlistItem.query.filter_by(bucket=1).first()
        self.assertEqual(item.bucket, 1)

    def test_update_item(self):
        self.assertEqual(self.test_item2.name, "testitem2")
        response = self.client.put("/bucketlists/{0}/items/{1}".format(self.test_bucket.id, self.test_item2.id),
                            data=json.dumps(dict(name="updated_name")), content_type="application/json",
                            headers={'Authorization': 'Token ' + self.login_test_user()[0]})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("Updated_Name", response_msg["Message"])


    def test_delete_item(self):
        pass

    def test_pagination(self):
        pass

    def test_search_by_name(self):
        pass



if __name__ == '__main__':
    unittest.main()
