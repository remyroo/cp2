import unittest
from flask import json
from tests.test_base import BaseTestCase


class APIAuthTests(BaseTestCase):
    """
    Test user creation and authentication.
    """
    def test_user_can_register(self):
        """Tests a new user can be added to the db."""
        response = self.client.post("/auth/register",
                                    data=json.dumps(dict(username="testjane",
                                                    password="test")),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)
        response_msg = json.loads(response.data)
        self.assertIn("Testjane", response_msg["Message"])

    def test_invalid_registration(self):
        """
        Tests error (Bad Request) is raised if
        username/password fields are empty.
        """
        response = self.client.post("/auth/register",
                                    data=json.dumps(dict(username="",
                                                    password="")),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 400)
        response_msg = json.loads(response.data)
        self.assertIn("required", response_msg["Message"])

    def test_valid_login_generates_token(self):
        """Tests token is generated on successful login."""
        response = self.client.post("/auth/register",
                                    data=json.dumps(dict(username="testjane",
                                                    password="test")),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)

        response = self.client.post("/auth/login",
                                    data=json.dumps(dict(username="testjane",
                                                    password="test")),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response_msg = json.loads(response.data)
        self.assertIn("Token", response_msg)

    def test_invalid_username_login(self):
        """
        Tests error (Unauthorized) is raised when
        login is attempted with an invalid username.
        """
        response = self.client.post("/auth/register",
                                    data=json.dumps(dict(username="invalid",
                                                    password="test")),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)

        response = self.client.post("/auth/login",
                                    data=json.dumps(dict(username="testjane",
                                                    password="invalid")),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 401)
        response_msg = json.loads(response.data)
        self.assertIn("Invalid", response_msg["Message"])

    def test_invalid_password_login(self):
        """
        Tests error (Unauthorized) is raised when
        login is attempted with an invalid password.
        """
        response = self.client.post("/auth/register",
                                    data=json.dumps(dict(username="testjane",
                                                    password="testpass")),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)

        response = self.client.post("/auth/login",
                                    data=json.dumps(dict(username="testjane",
                                                    password="invalid")),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 401)
        response_msg = json.loads(response.data)
        self.assertIn("Invalid", response_msg["Message"])


if __name__ == '__main__':
    unittest.main()
