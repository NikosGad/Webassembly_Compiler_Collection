import unittest

from rest_server import app, authentication
from rest_server.models import user_model

class ViewCompileTestCase(unittest.TestCase):
    """Testsuite for views/compile.py module."""
    @classmethod
    def setUpClass(cls):
        cls.user_info = {
            "username": "test_user_compile",
            "password": "12345a",
            "email": "test@mail.com"
        }

        cls.test_user = user_model.User(**cls.user_info)
        cls.test_user.id = cls.user_info["id"] = 1
        cls.test_user.create()

        cls.token_valid = authentication.Authentication.generate_token(1, 60)

    @classmethod
    def tearDownClass(cls):
        cls.test_user.delete()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_compile_store__unauthorized(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/compile/C/store",
        }

        with app.test_client() as c:
            response = c.post(**mock_request)

        self.assertEqual(response._status, "401 UNAUTHORIZED")
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.headers.get("WWW-Authenticate"), "Bearer realm=\"Access to user specific resources\"")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        self.assertEqual(response.get_json(), {"type": "AuthorizationViolation", "message": "Authorization Header is missing"})

    def test_compile__invalid_language(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/compile/invalid-language",
        }

        with app.test_client() as c:
            response = c.post(**mock_request)

        self.assertEqual(response._status, "400 BAD REQUEST")
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        self.assertEqual(response.get_json(), {"type": "LanguageNotSupportedError", "message": "Language invalid-language is not supported."})

    def test_compile_store__invalid_language(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/compile/invalid-language/store",
            "headers": {
                "Authorization": "Bearer " + self.token_valid
            },
        }

        with app.test_client() as c:
            response = c.post(**mock_request)

        self.assertEqual(response._status, "400 BAD REQUEST")
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        self.assertEqual(response.get_json(), {"type": "LanguageNotSupportedError", "message": "Language invalid-language is not supported."})
