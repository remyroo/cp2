import unittest
from flask import request, jsonify, json, current_app
from bucketlist.api import app, db, User, Bucketlist, BucketlistItem


class TestAPIBucketlists(unittest.TestCase):
    '''
    Test bucketlist interactions
    '''
    def login_test_user(self):
        data = {"username": "testuser", "password": "testpass"}
        test_user = User()
        test_user.import_data(data)
        test_user.set_password(test_user.password_hash)
        db.session.add(test_user)
        db.session.commit()
        response = self.client.post("/auth/login", data=json.dumps(
            dict(username="testuser", password="testpass")),
            content_type="application/json")
        response_msg = json.loads(response.data)
        return response_msg["Token"]

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tests/test.sqlite"
        app.config["TESTING"] = True
        self.client = app.test_client()
        db.create_all()
        self.login_test_user()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_add_new_bucketlist(self):
        response = self.client.post("/bucketlists/",
                                    data=json.dumps(dict(list_name="testbucket")), content_type="application/json",
                                    headers=self.login_test_user())
        self.assertEqual(response.status_code, 201)

    def test_return_all_bucketlists(self):
        response = self.client.get("/bucketlists/",
                                    data=json.dumps(content_type="application/json",
                                    headers=self.login_test_user()))
        self.assertEqual(response.status_code, 200)

    def test_get_bucketlist(self):
        pass

    def test_update_bucketlist(self):
        pass

    def test_delete_bucketlist(self):
        pass

    def test_add_new_item(self):
        pass

    def test_update_item(self):
        pass

    def test_delete_item(self):
        pass

    def test_pagination(self):
        pass

    def test_search_by_name(self):
        pass


if __name__ == '__main__':
    unittest.main()
