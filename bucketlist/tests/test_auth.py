import unittest
from flask import json
from bucketlist.api import app, db, User


class TestAPIAuth(unittest.TestCase):
    '''
    Test user creation and authentication
    '''
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tests/test.sqlite"
        app.config["TESTING"] = True
        self.client = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    def test_user_registration(self):
        '''
        Test a user can be created
        '''
        response = self.client.post("/auth/register",
                                 data=json.dumps(dict(username="testuser",
                                    password="testpass")), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        response_msg = json.loads(response.data)
        self.assertIn("Testuser", response_msg["Message"])

    def test_invalid_registration(self):
        '''
        Test error is raised if username/password is empty
        '''
        response = self.client.post("/auth/register",
                                 data=json.dumps(dict(username="",
                                    password="")), content_type="application/json")
        self.assertEqual(response.status_code, 500)

    def test_user_login_generates_token(self):
        '''
        First create a user then attempt to log them in.
        The token is autogenerated on login.
        '''
        data = {"username": "testuser", "password": "testpass"}
        test_user = User()
        test_user.import_data(data)
        test_user.set_password(test_user.password_hash)
        db.session.add(test_user)
        db.session.commit()

        response = self.client.post("/auth/login",
                                    data=json.dumps(dict(username="testuser",
                                        password="testpass")), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("token", response_msg["Token"])

    def test_invalid_login(self):
        '''
        Test invalid login attempt is unauthorized
        '''
        data = {"username": "testuser", "password": "testpass"}
        test_user = User()
        test_user.import_data(data)
        test_user.set_password(test_user.password_hash)
        db.session.add(test_user)
        db.session.commit()

        response = self.client.post("/auth/login",
                                    data=json.dumps(dict(username="testuser",
                                        password="invalid")), content_type="application/json")
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
