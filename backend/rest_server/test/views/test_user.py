import datetime
import unittest

from rest_server import app
from rest_server.models import user_model

class ViewUserTestCase(unittest.TestCase):
    """Testsuite for views/user.py module."""
    @classmethod
    def setUpClass(cls):
        cls.new_user_info = {
            "username": "test_user",
            "password": "12345a",
            "email": "test@mail.com"
        }

        cls.existing_user_info = {
            "username": "test_user_exists",
            "password": "12345a",
            "email": "test_user_exists@mail.com",
        }

        cls.test_existing_user = user_model.User(**cls.existing_user_info)
        cls.test_existing_user.create()

    @classmethod
    def tearDownClass(cls):
        cls.test_existing_user.delete()

    def tearDown(self):
        test_new_user = user_model.User.get_user_by_username(self.new_user_info["username"])
        if test_new_user:
            test_new_user.delete()

        test_all_users = user_model.User.get_all_users()
        if len(test_all_users) > 1:
            print("One or more testcases have unexpected leftovers in users table in DB.")
            for user in test_all_users:
                if user.username != "test_user_exists":
                    user.delete()

        test_all_users = user_model.User.get_all_users()
        if len(test_all_users) > 1:
            raise Exception("Failed to restore users table in DB.")

    def test_signup__valid(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/signup",
            "data": self.new_user_info,
        }

        with app.test_client() as c:
            response = c.post(**mock_request)

        self.assertEqual(response._status, "200 OK")
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        self.assertEqual(response.get_json(), {"message": "OK"})

    def test_signup__validation_errors(self):
        test_time = datetime.datetime.utcnow()

        invalid_user_schema_list = [
            {
                "id": 1,
                "username": "test username",
                "password": "12345a",
                "email": "test_user@email.com",
                "created_at": test_time,
                "updated_at": test_time,
                "extra field": True,
            },
            {
                "id": 1,
            },
            {
                "username": "a",
                "password": "1",
                "email": "test_user@email",
            },
            {
                "username": "a_",
                "password": "pass word",
                "email": "test_user",
            },
            {
                "username": "a_\n",
                "password": "pass\nword1",
                "email": "test user@email.com",
            },
            {
                "username": "a_\n a",
                "password": "1234\n5678a",
                "email": "test_user@email.com",
            },
            {
                "username": "a_ a",
                "password": "1234\t\t5678a",
                "email": "test_user@email.com",
            },
            {
                "username": "a_ αa", # Non-latin characters are not allowed in username
                "password": "1234 5678aα", # Non-latin characters are allowed in password
                "email": "test_user@email.com",
            },
        ]

        expected_response_list = [
            {
                "created_at": ["Unknown field."],
                "extra field": ["Unknown field."],
                "id": ["Unknown field."],
                "updated_at": ["Unknown field."],
            },
            {
                "email": ["Missing data for required field."],
                "id": ["Unknown field."],
                "password": ["Missing data for required field."],
                "username": ["Missing data for required field."],
            },
            {
                "email": ["Not a valid email address."],
                "password": [
                    "Password length must be at least 6.",
                    "Password must contain at least 1 latin letter(s)."
                ],
                "username": ["Username must contain only latin letters, numbers, _ and spaces. It must start and end with a letter. It must have length greater than 1."],
            },
            {
                "email": ["Not a valid email address."],
                "password": [
                    "Password must not contain white spaces.",
                    "Password must contain at least 1 number(s).",
                ],
                "username": ["Username must contain only latin letters, numbers, _ and spaces. It must start and end with a letter. It must have length greater than 1."],
            },
            {
                "email": ["Not a valid email address."],
                "password": ["Password must not contain white spaces."],
                "username": ["Username must contain only latin letters, numbers, _ and spaces. It must start and end with a letter. It must have length greater than 1."],
            },
            {
                "password": ["Password must not contain white spaces."],
                "username": ["Username must contain only latin letters, numbers, _ and spaces. It must start and end with a letter. It must have length greater than 1."],
            },
            {
                "password": ["Password must not contain white spaces."],
            },
            {
                "password": ["Password must not contain white spaces."],
                "username": ["Username must contain only latin letters, numbers, _ and spaces. It must start and end with a letter. It must have length greater than 1."],
            },
        ]

        self.assertEqual(len(invalid_user_schema_list), len(expected_response_list))

        for index, invalid_user_schema in enumerate(invalid_user_schema_list):
            mock_request = {
                "base_url": "http://127.0.0.1:8080",
                "path": "/api/signup",
                "data": invalid_user_schema,
            }

            with app.test_client() as c:
                response = c.post(**mock_request)

            self.assertEqual(response._status, "400 BAD REQUEST",
                msg="Failure with form: {form_dict}".format(
                    form_dict=invalid_user_schema
                )
            )
            self.assertEqual(response.headers.get("Content-Type"), "application/json",
                msg="Failure with form: {form_dict}".format(
                    form_dict=invalid_user_schema
                )
            )
            self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535",
                msg="Failure with form: {form_dict}".format(
                    form_dict=invalid_user_schema
                )
            )
            self.assertEqual(response.get_json(), {"type": "SignUpError", "message": expected_response_list[index]},
                msg="Failure with form: {form_dict}".format(
                    form_dict=invalid_user_schema
                )
            )

    def test_signup__username_exists_error(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/signup",
            "data": self.existing_user_info,
        }

        with app.test_client() as c:
            response = c.post(**mock_request)

        self.assertEqual(response._status, "400 BAD REQUEST")
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        self.assertEqual(response.get_json(), {"type": "UniqueUsernameViolation", "message": "Username test_user_exists already exists"})

    def test_signup__email_exists_error(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/signup",
            "data": {
                "username": "test_user_new",
                "password": "12345a",
                "email": "test_user_exists@mail.com",
            },
        }

        with app.test_client() as c:
            response = c.post(**mock_request)

        self.assertEqual(response._status, "400 BAD REQUEST")
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        self.assertEqual(response.get_json(), {"type": "UniqueEmailViolation", "message": "Email test_user_exists@mail.com already exists"})

    def test_login__valid(self):
        user_info_form_list = [
            {
                "username": "test_user_exists",
                "password": "12345a",
            },
            self.existing_user_info,
        ]

        for user_info_form in user_info_form_list:
            mock_request = {
                "base_url": "http://127.0.0.1:8080",
                "path": "/api/login",
                "data": user_info_form,
            }

            with app.test_client() as c:
                response = c.post(**mock_request)

            self.assertEqual(response._status, "200 OK")
            self.assertEqual(response.headers.get("Content-Type"), "application/json")
            self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")

            response_json = response.get_json()
            self.assertEqual(len(response_json.keys()), 2,
                msg="Response json does not contain exactly 2 keys: {response_json}".format(
                    response_json=response_json
                )
            )
            self.assertEqual(response_json.get("message"), "OK")
            self.assertIsNotNone(response_json.get("jwt"))
            self.assertIsInstance(response_json.get("jwt"), str)
            self.assertEqual(len(response_json.get("jwt").split(".")), 3, msg="JWToken should have three parts separated by a dot.")

    def test_login__missing_form_fields(self):
        user_info_form_list = [
            {},
            {
                "username": "test_user_exists",
            },
            {
                "password": "12345a",
            }
        ]

        for user_info_form in user_info_form_list:
            mock_request = {
                "base_url": "http://127.0.0.1:8080",
                "path": "/api/login",
                "data": user_info_form,
            }

            with app.test_client() as c:
                response = c.post(**mock_request)

            self.assertEqual(response._status, "400 BAD REQUEST")
            self.assertEqual(response.headers.get("Content-Type"), "application/json")
            self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
            self.assertEqual(response.get_json(), {"type": "LogInError", "message": "Both username and password are required to log in."})

    def test_login__invalid_form_fields(self):
        user_info_form_list = [
            {
                "username": "test_user",
                "password": "12345a",
            },
            {
                "username": "test_user_exists",
                "password": "non-matching-password",
            }
        ]

        for user_info_form in user_info_form_list:
            mock_request = {
                "base_url": "http://127.0.0.1:8080",
                "path": "/api/login",
                "data": user_info_form,
            }

            with app.test_client() as c:
                response = c.post(**mock_request)

            self.assertEqual(response._status, "400 BAD REQUEST")
            self.assertEqual(response.headers.get("Content-Type"), "application/json")
            self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
            self.assertEqual(response.get_json(), {"type": "LogInError", "message": "Username, password or both are incorrect."})
