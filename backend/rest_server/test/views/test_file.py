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

        cls.full_file_path = cls.mock_root_upload_path + "/1/mock_subpath"
        cls.file_name = "hello.c"

        cls.c_source_code_snippet_hello_c = os.path.dirname(__file__) + "/../test_source_code_snippets/hello.c"

        os.makedirs(cls.full_file_path)
        shutil.copyfile(cls.c_source_code_snippet_hello_c, cls.full_file_path + "/" + cls.file_name)

        handler = MockedCompilationHandler(cls.mock_language, cls.mock_root_upload_path)
        compilation_handlers_dictionary[cls.mock_language] = handler

        cls.user_info_1 = {
            "username": "test_user_view_file_1",
            "password": "12345a",
            "email":    "test1@mail.com"
        }

        cls.user_info_2 = {
            "username": "test_user_view_file_2",
            "password": "12345a",
            "email":    "test2@mail.com"
        }

        cls.file_info_1 = {
            "user_id":              1,
            "name":                 "hello.c",
            "directory":            "mock_subpath",
            "compilation_options":  ["mock_option_1", "mock_option_2"],
            "language":             cls.mock_language,
            "status":               "test_status_1",
        }

        cls.file_info_2 = {
            "user_id":              1,
            "name":                 "test_name_2",
            "directory":            "test_directory_2",
            "compilation_options":  [],
            "language":             "mock_language_2",
            "status":               "test_status_2",
        }

        cls.file_info_3 = {
            "user_id":              2,
            "name":                 "test_name_2",
            "directory":            "test_directory_3",
            "compilation_options":  [],
            "language":             cls.mock_language,
            "status":               "test_status_2",
        }

        cls.test_user_1 = user_model.User(**cls.user_info_1)
        cls.test_user_1.id = cls.user_info_1["id"] = 1
        cls.test_user_2 = user_model.User(**cls.user_info_2)
        cls.test_user_2.id = cls.user_info_2["id"] = 2

        cls.test_file_1 = file_model.SourceCodeFile(**cls.file_info_1)
        cls.test_file_1.id = cls.file_info_1["id"] = 1
        cls.test_file_2 = file_model.SourceCodeFile(**cls.file_info_2)
        cls.test_file_2.id = cls.file_info_2["id"] = 2
        cls.test_file_3 = file_model.SourceCodeFile(**cls.file_info_3)
        cls.test_file_3.id = cls.file_info_3["id"] = 3

        cls.test_user_1.create()
        cls.test_user_2.create()
        cls.test_file_1.create()
        cls.test_file_2.create()
        cls.test_file_3.create()

        cls.token_valid_1 = authentication.Authentication.generate_token(1, 60)

    @classmethod
    def tearDownClass(cls):
        cls.test_file_1.delete()
        cls.test_file_2.delete()
        cls.test_file_3.delete()
        cls.test_user_1.delete()
        cls.test_user_2.delete()

        del compilation_handlers_dictionary[cls.mock_language]

        if os.path.exists(cls.mock_root_upload_path):
            shutil.rmtree(cls.mock_root_upload_path)

    def setUp(self):
        pass

    def tearDown(self):
        pass

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

    def test_get_personal_files(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/files/all_personal",
            "headers": {
                "Authorization": "Bearer " + self.token_valid_1
            },
        }

        with app.test_client() as c:
            response = c.get(**mock_request)

        self.assertEqual(response._status, "200 OK")
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        response_json_as_dict = response.get_json()

        self.assertEqual(sorted(response_json_as_dict.keys()), sorted([self.file_info_1["language"], self.file_info_2["language"]]),
            msg="Dictionary of languages has different keys\nReturned: {returned}\nExpected= {expected}".format(
                returned=response_json_as_dict,
                expected=sorted([self.file_info_1["language"], self.file_info_2["language"]]),
            )
        )

        language_1_list = response_json_as_dict[self.file_info_1["language"]]
        language_2_list = response_json_as_dict[self.file_info_2["language"]]

        self.assertIsInstance(language_1_list, list)
        self.assertEqual(len(language_1_list), 1,
            msg="The list should contain only one file\nReturned: {returned}".format(
                returned=language_1_list
            )
        )
        self.assertIsInstance(language_2_list, list)
        self.assertEqual(len(language_2_list), 1,
            msg="The list should contain only one file\nReturned: {returned}".format(
                returned=language_2_list
            )
        )

        response_file_1 = language_1_list[0]
        response_file_2 = language_2_list[0]

        response_file_list = [response_file_1, response_file_2]
        test_file_list = [self.file_info_1, self.file_info_2]

        for i in range(2):
            self.assertEqual(len(response_file_list[i].keys()), len(test_file_list[i].keys()) + 2)
            self.assertEqual(response_file_list[i]["id"], test_file_list[i]["id"])
            self.assertEqual(response_file_list[i]["user_id"], test_file_list[i]["user_id"])
            self.assertEqual(response_file_list[i]["name"], test_file_list[i]["name"])
            self.assertEqual(response_file_list[i]["directory"], test_file_list[i]["directory"])
            self.assertEqual(response_file_list[i]["compilation_options"], test_file_list[i]["compilation_options"])
            self.assertEqual(response_file_list[i]["language"], test_file_list[i]["language"])
            self.assertEqual(response_file_list[i]["status"], test_file_list[i]["status"])
            self.assertIsInstance(response_file_list[i]["created_at"], str, msg="json_agg should convert the datetime to string")
            self.assertIsInstance(response_file_list[i]["updated_at"], str, msg="json_agg should convert the datetime to string")

class ViewFileDeleteTestCase(unittest.TestCase):
    """Testsuite for views/file.py module that checks the delete file view."""
    @classmethod
    def setUpClass(cls):
        cls.mock_language = "language_view_file"
        cls.mock_root_upload_path = "/results/language_view_file"

        cls.full_file_path = cls.mock_root_upload_path + "/1/mock_subpath"
        cls.file_name = "hello.c"

        cls.c_source_code_snippet_hello_c = os.path.dirname(__file__) + "/../test_source_code_snippets/hello.c"

        os.makedirs(cls.full_file_path)
        shutil.copyfile(cls.c_source_code_snippet_hello_c, cls.full_file_path + "/" + cls.file_name)

        handler = MockedCompilationHandler(cls.mock_language, cls.mock_root_upload_path)
        compilation_handlers_dictionary[cls.mock_language] = handler

        cls.user_info_1 = {
            "username": "test_user_view_file_1",
            "password": "12345a",
            "email":    "test1@mail.com"
        }

        cls.user_info_2 = {
            "username": "test_user_view_file_2",
            "password": "12345a",
            "email":    "test2@mail.com"
        }

        cls.file_info_1 = {
            "user_id":              1,
            "name":                 "hello.c",
            "directory":            "mock_subpath",
            "compilation_options":  ["mock_option_1", "mock_option_2"],
            "language":             cls.mock_language,
            "status":               "test_status_1",
        }

        cls.file_info_2 = {
        "user_id":              1,
        "name":                 "test_name_2",
        "directory":            "test_directory_2",
        "compilation_options":  [],
        "language":             cls.mock_language,
        "status":               "test_status_2",
        }

        cls.file_info_3 = {
        "user_id":              2,
        "name":                 "test_name_3",
        "directory":            "test_directory_3",
        "compilation_options":  [],
        "language":             cls.mock_language,
        "status":               "test_status_3",
        }

        cls.test_user_1 = user_model.User(**cls.user_info_1)
        cls.test_user_1.id = cls.user_info_1["id"] = 1
        cls.test_user_2 = user_model.User(**cls.user_info_2)
        cls.test_user_2.id = cls.user_info_2["id"] = 2

        cls.test_file_1 = file_model.SourceCodeFile(**cls.file_info_1)
        cls.test_file_1.id = cls.file_info_1["id"] = 1
        cls.test_file_2 = file_model.SourceCodeFile(**cls.file_info_2)
        cls.test_file_2.id = cls.file_info_2["id"] = 2
        cls.test_file_3 = file_model.SourceCodeFile(**cls.file_info_3)
        cls.test_file_3.id = cls.file_info_3["id"] = 3

        cls.test_user_1.create()
        cls.test_user_2.create()
        cls.test_file_1.create()
        cls.test_file_2.create()
        cls.test_file_3.create()

        cls.token_valid_1 = authentication.Authentication.generate_token(1, 60)

    @classmethod
    def tearDownClass(cls):
        test_all_files = file_model.SourceCodeFile.get_all_files()
        for file in test_all_files:
            file.delete()

        test_all_users = user_model.User.get_all_users()
        for user in test_all_users:
            user.delete()

        del compilation_handlers_dictionary[cls.mock_language]

        if os.path.exists(cls.mock_root_upload_path):
            shutil.rmtree(cls.mock_root_upload_path)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_delete_personal_file_directory(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/files/personal_file/1",
            "headers": {
                "Authorization": "Bearer " + self.token_valid_1
            },
        }

        with self.assertLogs(app.logger, level="INFO") as logs_list:
            with app.test_client() as c:
                response = c.delete(**mock_request)

        self.assertEqual(response._status, "200 OK")
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        self.assertEqual(response.get_json(), {"message": "OK"})
        self.assertEqual(os.listdir(self.mock_root_upload_path + "/1"), [])
        self.assertIsNone(file_model.SourceCodeFile.get_file_by_file_id_and_user_id(1, 1))

        self.assertEqual(len(logs_list.output), 2,
            msg="There are expected exactly 2 log messages: {logs_list}".format(
                logs_list=logs_list
            )
        )
        self.assertIn("INFO:", logs_list.output[0])
        self.assertIn("Deleted file from FS: " + str(self.test_file_1) + "\nin path: " + self.full_file_path, logs_list.output[0])
        self.assertIn("INFO:", logs_list.output[1])
        self.assertIn("Deleted file from DB: ", logs_list.output[1])

    def test_delete_personal_file_directory__invalid_file_id(self):
        invalid_file_id_list = [
            "alphanumerical_file_id",
            "-1",
            "0",
        ]

        for invalid_file_id in invalid_file_id_list:
            mock_request = {
                "base_url": "http://127.0.0.1:8080",
                "path": "/api/files/personal_file/" + invalid_file_id,
                "headers": {
                    "Authorization": "Bearer " + self.token_valid_1
                },
            }

            with app.test_client() as c:
                response = c.delete(**mock_request)

            self.assertEqual(response._status, "400 BAD REQUEST",
                msg="Failure with file_id: {file_id}".format(
                    file_id=invalid_file_id
                )
            )
            self.assertEqual(response.headers.get("Content-Type"), "application/json",
                msg="Failure with file_id: {file_id}".format(
                    file_id=invalid_file_id
                )
            )
            self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535",
                msg="Failure with file_id: {file_id}".format(
                    file_id=invalid_file_id
                )
            )
            self.assertEqual(response.get_json(), {"type": "FileIDTypeError", "message": "File ID value should be a positive integer"},
                msg="Failure with file_id: {file_id}".format(
                    file_id=invalid_file_id
                )
            )

    def test_delete_personal_file_directory__file_does_not_exist_in_db(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/files/personal_file/4",
            "headers": {
                "Authorization": "Bearer " + self.token_valid_1
            },
        }

        with app.test_client() as c:
            response = c.delete(**mock_request)

        self.assertEqual(response._status, "404 NOT FOUND")
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        self.assertEqual(response.get_json(), {"type": "FileNotFound", "message": "The file you are trying to delete does not exist"})

    def test_delete_personal_file_directory__delete_other_users_file(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/files/personal_file/3",
            "headers": {
                "Authorization": "Bearer " + self.token_valid_1
            },
        }

        with app.test_client() as c:
            response = c.delete(**mock_request)

        self.assertEqual(response._status, "404 NOT FOUND")
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        self.assertEqual(response.get_json(), {"type": "FileNotFound", "message": "The file you are trying to delete does not exist"})
        self.assertIsNotNone(file_model.SourceCodeFile.get_file_by_file_id_and_user_id(3, 2))

    def test_delete_personal_file_directory__inconsistency_file_exists_in_db_not_in_fs(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/files/personal_file/2",
            "headers": {
                "Authorization": "Bearer " + self.token_valid_1
            },
        }

        with self.assertLogs(app.logger, level="INFO") as logs_list:
            with app.test_client() as c:
                response = c.delete(**mock_request)

        self.assertEqual(response._status, "200 OK")
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        self.assertEqual(response.get_json(), {"message": "OK"})
        self.assertIsNone(file_model.SourceCodeFile.get_file_by_file_id_and_user_id(2, 1))

        self.assertEqual(len(logs_list.output), 2,
            msg="There are expected exactly 2 log messages: {logs_list}".format(
                logs_list=logs_list
            )
        )
        self.assertIn("ERROR:", logs_list.output[0])
        self.assertIn("Inconsistency during delete of file: ", logs_list.output[0])
        self.assertIn("INFO:", logs_list.output[1])
        self.assertIn("Deleted file from DB: ", logs_list.output[1])
