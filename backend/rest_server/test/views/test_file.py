import os
import shutil
import unittest
from flask import request

from rest_server import app, authentication
from rest_server.compile import compilation_handlers_dictionary
from rest_server.compile.compile import CompilationHandler
from rest_server.models import file_model, user_model

class MockedCompilationHandler(CompilationHandler):
    """MockedCompilationHandler class mocks up all the CompilationHandler methods except the compile method."""
    def _generate_file_subpath(self, client_file):
        return "mock_subpath"

    def compilation_options_parser(self, *args, **kwargs):
        return ["mock_option_1", "mock_option_2"], "mock_output_name"

    def compilation_command_generator(self, *args, **kwargs):
        return ["ls", "non-existing-path"]

    def results_zip_appender(self, *args, **kwargs):
        pass

class ViewFileTestCase(unittest.TestCase):
    """Testsuite for views/file.py module."""
    @classmethod
    def setUpClass(cls):
        cls.mock_language = "language_view_file"
        cls.mock_root_upload_path = "/results/language_view_file"
        os.makedirs(cls.mock_root_upload_path)

        handler = MockedCompilationHandler(cls.mock_language, cls.mock_root_upload_path)
        compilation_handlers_dictionary[cls.mock_language] = handler

        cls.c_source_code_snippet_hello_c = os.path.dirname(__file__) + "/../test_source_code_snippets/hello.c"

        cls.user_info = {
            "username": "test_user_compile",
            "password": "12345a",
            "email": "test@mail.com"
        }

        cls.test_user = user_model.User(**cls.user_info)
        cls.test_user.id = cls.user_info["id"] = 1
        cls.test_user.create()

        cls.token_valid_1 = authentication.Authentication.generate_token(1, 60)

    @classmethod
    def tearDownClass(cls):
        cls.test_user.delete()

        del compilation_handlers_dictionary[cls.mock_language]

        if os.path.exists(cls.mock_root_upload_path):
            shutil.rmtree(cls.mock_root_upload_path)

    def setUp(self):
        self.full_file_path = self.mock_root_upload_path + "/1/mock_subpath"
        self.file_name = "hello.c"

        os.makedirs(self.full_file_path)
        shutil.copyfile(self.c_source_code_snippet_hello_c, self.full_file_path + "/" + self.file_name)

    def tearDown(self):
        if os.path.exists(self.full_file_path):
            shutil.rmtree(self.full_file_path)

    def test_get_personal_file_content(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/files/personal_file_content",
            "headers": {
                "Authorization": "Bearer " + self.token_valid_1
            },
            "query_string": {
                "language": self.mock_language,
                "directory": "mock_subpath",
                "name": self.file_name,
            }
        }

        with app.test_client() as c:
            response = c.get(**mock_request)

        self.assertEqual(response._status, "200 OK")
        self.assertEqual(response.headers.get("Content-Type"), "text/plain; charset=utf-8")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        self.assertEqual(response.headers.get("Content-Disposition"), "attachment; filename=" + self.file_name)

        response_file_content = response.get_data()
        with open(self.c_source_code_snippet_hello_c, "rb") as expected_file:
            expected_file_content = expected_file.read()
            self.assertEqual(response_file_content, expected_file_content)

    def test_get_personal_file_content__unauthorized(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/files/personal_file_content",
            "query_string": {
                "language": self.mock_language,
                "directory": "mock_subpath",
                "name": self.file_name,
            }
        }

        with app.test_client() as c:
            response = c.get(**mock_request)

        self.assertEqual(response._status, "401 UNAUTHORIZED")
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.headers.get("WWW-Authenticate"), "Bearer realm=\"Access to user specific resources\"")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        self.assertEqual(response.get_json(), {"type": "AuthorizationViolation", "message": "Authorization Header is missing"})

    def test_get_personal_file_content__invalid_language(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/files/personal_file_content",
            "headers": {
                "Authorization": "Bearer " + self.token_valid_1
            },
            "query_string": {
                "language": "invalid-language",
                "directory": "mock_subpath",
                "name": self.file_name,
            }
        }

        with app.test_client() as c:
            response = c.get(**mock_request)

        self.assertEqual(response._status, "400 BAD REQUEST")
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        self.assertEqual(response.get_json(), {"type": "GetFileError", "message": "Language invalid-language is not supported."})

    def test_get_personal_file_content__missing_query_parameters(self):
        query_parameters_list = [
            {},
            {
                "language": "invalid-language",
            },
            {
                "directory": "mock_subpath",
            },
            {
                "name": self.file_name,
            },
            {
                "language": "invalid-language",
                "directory": "mock_subpath",
            },
            {
                "language": "invalid-language",
                "name": self.file_name,
            },
            {
                "directory": "mock_subpath",
                "name": self.file_name,
            },
        ]

        for query_parameters in query_parameters_list:
            mock_request = {
                "base_url": "http://127.0.0.1:8080",
                "path": "/api/files/personal_file_content",
                "headers": {
                    "Authorization": "Bearer " + self.token_valid_1
                },
                "query_string": query_parameters
            }

            with app.test_client() as c:
                response = c.get(**mock_request)

            self.assertEqual(response._status, "400 BAD REQUEST",
                msg="Failure with query parameters: {query_parameters_dict}".format(
                    query_parameters_dict=query_parameters
                )
            )
            self.assertEqual(response.headers.get("Content-Type"), "application/json",
                msg="Failure with query parameters: {query_parameters_dict}".format(
                    query_parameters_dict=query_parameters
                )
            )
            self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535",
                msg="Failure with query parameters: {query_parameters_dict}".format(
                    query_parameters_dict=query_parameters
                )
            )
            self.assertEqual(response.get_json(), {"type": "GetFileError", "message": "A language, a directory and a name query parameters should be provided."},
                msg="Failure with query parameters: {query_parameters_dict}".format(
                    query_parameters_dict=query_parameters
                )
            )

    def test_get_personal_file_content__extra_query_parameters(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/files/personal_file_content",
            "headers": {
                "Authorization": "Bearer " + self.token_valid_1
            },
            "query_string": {
                "language": self.mock_language,
                "directory": "mock_subpath",
                "name": self.file_name,
                "extra_1": True,
                "hack": "hack",
            }
        }

        with app.test_client() as c:
            response = c.get(**mock_request)

        self.assertEqual(response._status, "200 OK")
        self.assertEqual(response.headers.get("Content-Type"), "text/plain; charset=utf-8")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        self.assertEqual(response.headers.get("Content-Disposition"), "attachment; filename=" + self.file_name)

        response_file_content = response.get_data()
        with open(self.c_source_code_snippet_hello_c, "rb") as expected_file:
            expected_file_content = expected_file.read()
            self.assertEqual(response_file_content, expected_file_content)

    def test_get_personal_file_content__file_not_found(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/files/personal_file_content",
            "headers": {
                "Authorization": "Bearer " + self.token_valid_1
            },
            "query_string": {
                "language": self.mock_language,
                "directory": "mock_subpath",
                "name": "non-existing-file",
            }
        }

        with app.test_client() as c:
            response = c.get(**mock_request)

        self.assertEqual(response._status, "404 NOT FOUND")
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        self.assertEqual(response.get_json(), {"type": "FileNotFound", "message": "The file could not be found. Are you sure it should exists? If this was an existing file that belonged to you, please try to delete it and re-upload it."})

    def test_get_personal_file_content__insecured_parameters(self):
        insecured_query_parameters_list = [
            {
                "language": self.mock_language,
                "directory": "../mock_subpath",
                "name": "../hello.c",
            },
            {
                "language": self.mock_language,
                "directory": "../1/mock_subpath",
                "name": "hello.c",
            },
            {
                "language": self.mock_language,
                "directory": "../1/./mock_subpath",
                "name": "../mock_subpath/hello.c",
            },
        ]

        expected_response_status_list = [
            "200 OK",
            "404 NOT FOUND",
            "404 NOT FOUND",
        ]

        self.assertEqual(len(insecured_query_parameters_list), len(expected_response_status_list))

        for index, insecured_query_parameters in enumerate(insecured_query_parameters_list):
            mock_request = {
                "base_url": "http://127.0.0.1:8080",
                "path": "/api/files/personal_file_content",
                "headers": {
                    "Authorization": "Bearer " + self.token_valid_1
                },
                "query_string": insecured_query_parameters
            }

            with app.test_client() as c:
                response = c.get(**mock_request)

            self.assertEqual(response._status, expected_response_status_list[index],
                msg="Failure with query parameters: {query_parameters_dict}".format(
                    query_parameters_dict=insecured_query_parameters
                )
            )
