import os
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

        cls.c_source_code_snippet_hello_c = os.path.dirname(__file__) + "/../test_source_code_snippets/hello.c"

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

    def test_compile_C__missing_query_parameters(self):
        data_list = [
            {},
            {
                "code": (self.c_source_code_snippet_hello_c, None),
            },
            {
                "compilation_options": '{"optimization_level": "O2", "iso_standard": "gnu11", "suppress_warnings": true, "output_filename": "-----hello"}',
            },
        ]

        for data in data_list:
            mock_request = {
                "base_url": "http://127.0.0.1:8080",
                "path": "/api/compile/C",
                "data": data,
            }

            with app.test_client() as c:
                response = c.post(**mock_request)

            self.assertEqual(response._status, "400 BAD REQUEST")
            self.assertEqual(response.headers.get("Content-Type"), "application/json")
            self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
            self.assertEqual(response.get_json(), {"type": "IncorrectCompileBodyError", "message": "A form data should be provided that contains a file with key 'code' and a compilation options json with key 'compilation_options'."})

    def test_compile_store_C__missing_query_parameters(self):
        data_list = [
            {},
            {
                "code": (self.c_source_code_snippet_hello_c, None),
            },
            {
                "compilation_options": '{"optimization_level": "O2", "iso_standard": "gnu11", "suppress_warnings": true, "output_filename": "-----hello"}',
            },
        ]

        for data in data_list:
            mock_request = {
                "base_url": "http://127.0.0.1:8080",
                "path": "/api/compile/C/store",
                "headers": {
                    "Authorization": "Bearer " + self.token_valid
                },
                "data": data,
            }

            with app.test_client() as c:
                response = c.post(**mock_request)

            self.assertEqual(response._status, "400 BAD REQUEST")
            self.assertEqual(response.headers.get("Content-Type"), "application/json")
            self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
            self.assertEqual(response.get_json(), {"type": "IncorrectCompileBodyError", "message": "A form data should be provided that contains a file with key 'code' and a compilation options json with key 'compilation_options'."})
