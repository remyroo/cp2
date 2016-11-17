import unittest
from flask import json
from bucketlist.api import app, db, User, Bucketlist


class TestAPIBucketlists(unittest.TestCase):
    '''
    Test bucketlist interactions
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

    def create_test_bucketlists(self):
        data = {"list_name": "testbucketlist"}
        test_bucket = Bucketlist()
        test_bucket.import_data(data)
        test_bucket.created_by = self.login_test_user()[1]

        data2 = {"list_name": "testbucketlist2"}
        test_bucket2 = Bucketlist()
        test_bucket2.import_data(data2)
        test_bucket2.created_by = test_bucket.created_by

        db.session.add(test_bucket)
        db.session.add(test_bucket2)
        db.session.commit()
        return test_bucket, test_bucket2

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tests/test.sqlite"
        app.config["TESTING"] = True
        self.client = app.test_client()
        db.create_all()
        self.create_test_bucketlists()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_add_new_bucketlist(self):
        response = self.client.post("/bucketlists/",
                                    data=json.dumps(dict(list_name="testbucket")), content_type="application/json",
                                    headers={'Authorization': 'Token ' + self.login_test_user()[0]})
        self.assertEqual(response.status_code, 201)
        response_msg = json.loads(response.data)
        self.assertIn("Testbucket", response_msg["Message"])

    def test_return_all_bucketlists(self):
        response = self.client.get("/bucketlists/",
                                    content_type="application/json",
                                    headers={'Authorization': 'Token ' + self.login_test_user()[0]})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("testbucketlist", response_msg["All bucketlists"][0]["list_name"])

    def test_get_bucketlist(self):
        response = self.client.get("/bucketlists/1",
                                content_type="application/json",
                                headers={'Authorization': 'Token ' + self.login_test_user()[0]})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("testbucketlist", response_msg["Bucketlist"]["list_name"])

    def test_update_bucketlist(self):
        self.assertEqual(self.create_test_bucketlists()[1].list_name, "testbucketlist2")
        response = self.client.put("/bucketlists/2",
                            data=json.dumps(dict(list_name="updated_name")), content_type="application/json",
                            headers={'Authorization': 'Token ' + self.login_test_user()[0]})
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("Updated_Name", response_msg["Message"])

    def test_delete_bucketlist(self):
        self.assertEqual(self.create_test_bucketlists()[0].list_name, "testbucketlist")
        response = self.client.delete("/bucketlists/1",
                            content_type="application/json",
                            headers={'Authorization': 'Token ' + self.login_test_user()[0]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Bucketlist.query.get(1), None)


if __name__ == '__main__':
    unittest.main()
