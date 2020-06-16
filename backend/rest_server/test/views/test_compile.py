import filecmp
import io
import os
import shutil
import unittest
from zipfile import ZipFile

from rest_server import app, authentication
from rest_server.models import user_model, file_model
from rest_server.compile import compilation_handlers_dictionary

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
        cls.c_source_code_snippet_hello_error_c = os.path.dirname(__file__) + "/../test_source_code_snippets/hello_error.c"

        cls.handler_c = compilation_handlers_dictionary["C"]

    @classmethod
    def tearDownClass(cls):
        cls.test_user.delete()

        for entry in os.listdir(cls.handler_c.root_upload_path):
            entry_path = cls.handler_c.root_upload_path + "/" + entry
            if os.path.isdir(entry_path):
                shutil.rmtree(entry_path)
            else:
                os.remove(entry_path)

        test_all_files = file_model.SourceCodeFile.get_all_files()
        for file in test_all_files:
            file.delete()

    def setUp(self):
        root_upload_path_list = os.listdir(self.handler_c.root_upload_path)

        if root_upload_path_list != []:
            raise Exception(
                "Path {path} is not empty: {root_upload_path_list}".format(
                    path=self.handler_c.root_upload_path,
                    root_upload_path_list=root_upload_path_list
                )
            )

        test_all_files = file_model.SourceCodeFile.get_all_files()
        if test_all_files != []:
            raise Exception("There are leftovers in source_code_files table in DB")

    def tearDown(self):
        for entry in os.listdir(self.handler_c.root_upload_path):
            entry_path = self.handler_c.root_upload_path + "/" + entry
            if os.path.isdir(entry_path):
                shutil.rmtree(entry_path)
            else:
                os.remove(entry_path)

        test_all_files = file_model.SourceCodeFile.get_all_files()
        for file in test_all_files:
            file.delete()

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

    def test_compile_and_compile_store__invalid_language(self):
        mock_request_list = [
            {
                "base_url": "http://127.0.0.1:8080",
                "path": "/api/compile/invalid-language",
            },
            {
                "base_url": "http://127.0.0.1:8080",
                "path": "/api/compile/invalid-language/store",
                "headers": {
                    "Authorization": "Bearer " + self.token_valid
                },
            }
        ]

        for mock_request in mock_request_list:
            with app.test_client() as c:
                response = c.post(**mock_request)

            self.assertEqual(response._status, "400 BAD REQUEST")
            self.assertEqual(response.headers.get("Content-Type"), "application/json")
            self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
            self.assertEqual(response.get_json(), {"type": "LanguageNotSupportedError", "message": "Language invalid-language is not supported."})

    def test_compile_C_and_compile_store_C__missing_form_and_files_parameters(self):
        data_list = [
            {},
            {
                "code": (self.c_source_code_snippet_hello_c, None),
            },
            {
                "compilation_options": '{"optimization_level": "O2", "iso_standard": "gnu11", "suppress_warnings": true, "output_filename": "-----hello"}',
            },
        ]

        mock_request_list = [
            {
                "base_url": "http://127.0.0.1:8080",
                "path": "/api/compile/C",
            },
            {
                "base_url": "http://127.0.0.1:8080",
                "path": "/api/compile/C/store",
                "headers": {
                    "Authorization": "Bearer " + self.token_valid
                },
            }
        ]

        for data in data_list:
            for mock_request in mock_request_list:
                mock_request["data"] = data

                with app.test_client() as c:
                    response = c.post(**mock_request)

                self.assertEqual(response._status, "400 BAD REQUEST")
                self.assertEqual(response.headers.get("Content-Type"), "application/json")
                self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
                self.assertEqual(response.get_json(), {"type": "IncorrectCompileBodyError", "message": "A form data should be provided that contains a file with key 'code' and a compilation options json with key 'compilation_options'."})

    def test_compile_C__valid(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/compile/C",
            "data": {
                "code": (self.c_source_code_snippet_hello_c, "hello.c"),
                "compilation_options": '{"optimization_level": "O2", "iso_standard": "gnu11", "suppress_warnings": true, "output_filename": "-----hello"}',
            },
        }

        with app.test_client() as c:
            response = c.post(**mock_request)

        self.assertEqual(response._status, "200 OK")
        self.assertEqual(response.headers.get("Content-Type"), "application/zip")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        self.assertEqual(response.headers.get("Content-Disposition"), "attachment; filename=results.zip")

        root_upload_path_list = os.listdir(self.handler_c.root_upload_path)
        self.assertEqual(root_upload_path_list, ["unknown"],
            msg="Path {path} does not contain only the unknown folder: {root_upload_path_list}".format(
                path=self.handler_c.root_upload_path,
                root_upload_path_list=root_upload_path_list
            )
        )

        unknown_directory = self.handler_c.root_upload_path + "/unknown"
        unknown_directory_list = os.listdir(unknown_directory)
        self.assertEqual(len(unknown_directory_list), 1,
            msg="Path {path} does not contain exactly one level_1 uploaded file directory: {entry_list}".format(
                path=unknown_directory,
                entry_list=unknown_directory_list
            )
        )

        unknown_directory_level_1 = unknown_directory + "/" + unknown_directory_list[0]
        unknown_directory_level_1_list = os.listdir(unknown_directory_level_1)
        self.assertEqual(len(unknown_directory_level_1_list), 1,
            msg="Path {path} does not contain only the level_2 file directory: {entry_list}".format(
                path=unknown_directory_level_1,
                entry_list=unknown_directory_level_1_list
            )
        )

        uploaded_file_directory = unknown_directory_level_1 + "/" + unknown_directory_level_1_list[0]
        uploaded_file_directory_list = os.listdir(uploaded_file_directory)
        self.assertEqual(len(uploaded_file_directory_list), 5,
            msg="Path {path} does not contain exactly 5 files: {entry_list}".format(
                path=uploaded_file_directory,
                entry_list=uploaded_file_directory_list
            )
        )
        self.assertIn("hello.c", uploaded_file_directory_list)
        self.assertIn("hello.html", uploaded_file_directory_list)
        self.assertIn("hello.js", uploaded_file_directory_list)
        self.assertIn("hello.wasm", uploaded_file_directory_list)
        self.assertIn("results.zip", uploaded_file_directory_list)
        self.assertTrue(filecmp.cmp(uploaded_file_directory + "/hello.c", self.c_source_code_snippet_hello_c))
        self.assertTrue(os.stat(uploaded_file_directory + "/hello.html").st_size != 0)
        self.assertTrue(os.stat(uploaded_file_directory + "/hello.js").st_size != 0)
        self.assertTrue(os.stat(uploaded_file_directory + "/hello.wasm").st_size != 0)

        with ZipFile(file=uploaded_file_directory + "/results.zip", mode="r") as file_system_zip:
            self.assertIsNone(file_system_zip.testzip())
            self.assertEqual(file_system_zip.namelist(), ["hello.html", "hello.js", "hello.wasm"])
            file_system_zip_infolist = file_system_zip.infolist()
            self.assertEqual(os.stat(uploaded_file_directory + "/hello.html").st_size, file_system_zip_infolist[0].file_size)
            self.assertEqual(os.stat(uploaded_file_directory + "/hello.js").st_size, file_system_zip_infolist[1].file_size)
            self.assertEqual(os.stat(uploaded_file_directory + "/hello.wasm").st_size, file_system_zip_infolist[2].file_size)

            with io.BytesIO(response.get_data()) as in_memory_response_zip:
                with ZipFile(in_memory_response_zip, 'r') as response_zip:
                    self.assertIsNone(response_zip.testzip())
                    self.assertEqual(response_zip.namelist(), ["hello.html", "hello.js", "hello.wasm"])
                    response_zip_infolist = response_zip.infolist()

                    self.assertEqual(file_system_zip_infolist[0].file_size, response_zip_infolist[0].file_size,
                        msg="HTML files do not have the same size inside the two zip files"
                    )
                    self.assertEqual(file_system_zip_infolist[1].file_size, response_zip_infolist[1].file_size,
                        msg="JS files do not have the same size inside the two zip files"
                    )
                    self.assertEqual(file_system_zip_infolist[2].file_size, response_zip_infolist[2].file_size,
                        msg="WASM files do not have the same size inside the two zip files"
                    )

    def test_compile_store_C__valid(self):
        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/compile/C/store",
            "headers": {
                "Authorization": "Bearer " + self.token_valid
            },
            "data": {
                "code": (self.c_source_code_snippet_hello_c, "hello.c"),
                "compilation_options": '{"optimization_level": "O2", "iso_standard": "gnu11", "suppress_warnings": true, "output_filename": "-----hello"}',
            },
        }

        with app.test_client() as c:
            response = c.post(**mock_request)

        self.assertEqual(response._status, "200 OK")
        self.assertEqual(response.headers.get("Content-Type"), "application/zip")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3535")
        self.assertEqual(response.headers.get("Content-Disposition"), "attachment; filename=results.zip")

        root_upload_path_list = os.listdir(self.handler_c.root_upload_path)
        self.assertEqual(root_upload_path_list, [str(self.user_info["id"])],
            msg="Path {path} does not contain only the '{user_id}' folder: {root_upload_path_list}".format(
                path=self.handler_c.root_upload_path,
                user_id=self.user_info["id"],
                root_upload_path_list=root_upload_path_list
            )
        )

        user_directory = self.handler_c.root_upload_path + "/" + str(self.user_info["id"])
        user_directory_list = os.listdir(user_directory)
        self.assertEqual(len(user_directory_list), 1,
            msg="Path {path} does not contain exactly one level_1 uploaded file directory: {entry_list}".format(
                path=user_directory,
                entry_list=user_directory_list
            )
        )

        user_directory_level_1 = user_directory + "/" + user_directory_list[0]
        user_directory_level_1_list = os.listdir(user_directory_level_1)
        self.assertEqual(len(user_directory_level_1_list), 1,
            msg="Path {path} does not contain only the level_2 file directory: {entry_list}".format(
                path=user_directory_level_1,
                entry_list=user_directory_level_1_list
            )
        )

        uploaded_file_directory = user_directory_level_1 + "/" + user_directory_level_1_list[0]
        uploaded_file_directory_list = os.listdir(uploaded_file_directory)
        self.assertEqual(len(uploaded_file_directory_list), 5,
            msg="Path {path} does not contain exactly 5 files: {entry_list}".format(
                path=uploaded_file_directory,
                entry_list=uploaded_file_directory_list
            )
        )
        self.assertIn("hello.c", uploaded_file_directory_list)
        self.assertIn("hello.html", uploaded_file_directory_list)
        self.assertIn("hello.js", uploaded_file_directory_list)
        self.assertIn("hello.wasm", uploaded_file_directory_list)
        self.assertIn("results.zip", uploaded_file_directory_list)
        self.assertTrue(filecmp.cmp(uploaded_file_directory + "/hello.c", self.c_source_code_snippet_hello_c))
        self.assertTrue(os.stat(uploaded_file_directory + "/hello.html").st_size != 0)
        self.assertTrue(os.stat(uploaded_file_directory + "/hello.js").st_size != 0)
        self.assertTrue(os.stat(uploaded_file_directory + "/hello.wasm").st_size != 0)

        with ZipFile(file=uploaded_file_directory + "/results.zip", mode="r") as file_system_zip:
            self.assertIsNone(file_system_zip.testzip())
            self.assertEqual(file_system_zip.namelist(), ["hello.html", "hello.js", "hello.wasm"])
            file_system_zip_infolist = file_system_zip.infolist()
            self.assertEqual(os.stat(uploaded_file_directory + "/hello.html").st_size, file_system_zip_infolist[0].file_size)
            self.assertEqual(os.stat(uploaded_file_directory + "/hello.js").st_size, file_system_zip_infolist[1].file_size)
            self.assertEqual(os.stat(uploaded_file_directory + "/hello.wasm").st_size, file_system_zip_infolist[2].file_size)

            with io.BytesIO(response.get_data()) as in_memory_response_zip:
                with ZipFile(in_memory_response_zip, 'r') as response_zip:
                    self.assertIsNone(response_zip.testzip())
                    self.assertEqual(response_zip.namelist(), ["hello.html", "hello.js", "hello.wasm"])
                    response_zip_infolist = response_zip.infolist()

                    self.assertEqual(file_system_zip_infolist[0].file_size, response_zip_infolist[0].file_size,
                        msg="HTML files do not have the same size inside the two zip files"
                    )
                    self.assertEqual(file_system_zip_infolist[1].file_size, response_zip_infolist[1].file_size,
                        msg="JS files do not have the same size inside the two zip files"
                    )
                    self.assertEqual(file_system_zip_infolist[2].file_size, response_zip_infolist[2].file_size,
                        msg="WASM files do not have the same size inside the two zip files"
                    )

        test_all_files = file_model.SourceCodeFile.get_all_files()
        self.assertEqual(len(test_all_files), 1,
            msg="There is not exactly 1 file in DB: {files}".format(
                files=test_all_files
            )
        )
