import datetime
import filecmp
import hashlib
import io
import os
import shutil
import unittest
from zipfile import ZipFile

from flask import request

from rest_server import app
from rest_server.compile.compile import CompilationHandler
from rest_server.models import file_model

CURRENT_TEST_FILE_PATH = os.path.dirname(__file__) + "/test_compile.py"

class NonAbstractCompilationHandler(CompilationHandler):
    """NonAbstractCompilationHandler class implements dummy methods for the abstract methods."""
    def compilation_options_parser(self, *args, **kwargs):
        return [], "mock_output_name"

    def compilation_command_generator(self, *args, **kwargs):
        return []

    def results_zip_appender(self, *args, **kwargs):
        pass

class MockedCompilationHandler(NonAbstractCompilationHandler):
    """MockedCompilationHandler class mocks up all the CompilationHandler methods except the compile method."""
    def generate_file_subpath(self, client_file):
        return "mock_subpath"

class MockedCompilationHandlerWStdout(MockedCompilationHandler):
    """MockedCompilationHandlerWStdout class writes only in stdout with the compile method."""
    def compilation_command_generator(self, *args, **kwargs):
        return ["ls", CURRENT_TEST_FILE_PATH]

class MockedCompilationHandlerWStderr(MockedCompilationHandler):
    """MockedCompilationHandlerWStderr class writes only in stderr with the compile method."""
    def compilation_command_generator(self, *args, **kwargs):
        return ["ls", "non-existing-path"]

class MockedCompilationHandlerWStdoutWStderr(MockedCompilationHandler):
    """MockedCompilationHandlerWStdoutWStderr class writes in stdout and in stderr with the compile method."""
    def compilation_command_generator(self, *args, **kwargs):
        return ["ls", CURRENT_TEST_FILE_PATH, "non-existing-path"]

class CompileTestCase(unittest.TestCase):
    """Testsuite for compile/compile.py module."""
    @classmethod
    def setUpClass(cls):
        cls.mock_language = "language"
        cls.mock_root_upload_path = "/results/language"
        cls.c_source_code_snippet_hello_c = os.path.dirname(__file__) + "/../test_source_code_snippets/hello.c"

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.mock_root_upload_path):
            shutil.rmtree(cls.mock_root_upload_path)

    def setUp(self):
        if os.path.exists(self.mock_root_upload_path):
            raise Exception("Path {path} already exists before the testcase is executed".format(path=self.mock_root_upload_path))

    def tearDown(self):
        if os.path.exists(self.mock_root_upload_path):
            shutil.rmtree(self.mock_root_upload_path)

    def test_CompilationHandler_generate_file_subpath(self):
        handler = NonAbstractCompilationHandler(self.mock_language, self.mock_root_upload_path)

        with open(self.c_source_code_snippet_hello_c, "rb") as test_file:
            result = handler.generate_file_subpath(test_file)

            expected_sha256_hash = hashlib.sha256(test_file.read()).hexdigest()

        self.assertIsInstance(result, str)
        self.assertIn("_", result)
        self.assertNotEqual("/", result[-1])

        result_split = result.split("_")
        self.assertEqual(len(result_split), 2,
            msg="Subpath does not contain exactly two parts separeted by underscore: {subpath}".format(
                subpath=result
            )
        )
        self.assertIsInstance(datetime.datetime.strptime(result_split[0], "%Y%m%d%H%M%S%f"), datetime.datetime)
        self.assertEqual(result_split[1], expected_sha256_hash)

    def test_CompilationHandler_compile__invalid_compilation_options(self):
        handler = MockedCompilationHandlerWStdout(self.mock_language, self.mock_root_upload_path)
        compilation_options_json_list = [
            'key: rue',
            '{',
            '{key: value}',
            '{"key": "value}',
            '{"key": v"alue}',
            '{"key": True}',
        ]

        for compilation_options_json in compilation_options_json_list:
            mock_request = {
                "base_url": "http://127.0.0.1:8080",
                "path": "/api/test/compile/method",
                "data": {
                    "code": (self.c_source_code_snippet_hello_c, "hello.c"),
                    "compilation_options": compilation_options_json,
                },
            }

            with app.test_request_context(**mock_request):
                response, response_status = handler.compile(request.files["code"], request.form["compilation_options"])

            self.assertEqual(response_status, 400)
            self.assertEqual(response.headers.get("Content-Type"), "application/json")
            self.assertEqual(response.response[0], b"{\"message\":\"Bad JSON Format Error\",\"type\":\"JSONParseError\"}\n")

    def test_CompilationHandler_compile__subpath_exists(self):
        handler = MockedCompilationHandlerWStdout(self.mock_language, self.mock_root_upload_path)

        os.makedirs(self.mock_root_upload_path + "/unknown/mock_subpath")

        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/test/compile/method",
            "data": {
                "code": (self.c_source_code_snippet_hello_c, "hello.c"),
                "compilation_options": '{}',
            },
        }

        with app.test_request_context(**mock_request):
            response, response_status = handler.compile(request.files["code"], request.form["compilation_options"])

        self.assertEqual(response_status, 400)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.response[0], b"{\"message\":\"The uploaded file already exists\",\"type\":\"FileExistsError\"}\n")

    def test_CompilationHandler_compile__with_stdout(self):
        handler = MockedCompilationHandlerWStdout(self.mock_language, self.mock_root_upload_path)

        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/test/compile/method",
            "data": {
                "code": (self.c_source_code_snippet_hello_c, "hello.c"),
                "compilation_options": '{}',
            },
        }

        with app.test_request_context(**mock_request):
            response = handler.compile(request.files["code"], request.form["compilation_options"])

        self.assertEqual(response._status, "200 OK")
        self.assertEqual(response.headers.get("Content-Type"), "application/zip")
        self.assertEqual(response.headers.get("Content-Disposition"), "attachment; filename=results.zip")

        root_upload_path_list = os.listdir(self.mock_root_upload_path)
        self.assertEqual(root_upload_path_list, ["unknown"],
            msg="Path {path} does not contain only the unknown folder: {root_upload_path_list}".format(
                path=self.mock_root_upload_path,
                root_upload_path_list=root_upload_path_list
            )
        )

        unknown_directory = self.mock_root_upload_path + "/unknown"
        unknown_directory_list = os.listdir(unknown_directory)
        self.assertEqual(unknown_directory_list, ["mock_subpath"],
            msg="Path {path} does not contain only the mock_subpath file directory: {entry_list}".format(
                path=unknown_directory,
                entry_list=unknown_directory_list
            )
        )

        uploaded_file_directory = unknown_directory + "/mock_subpath"
        uploaded_file_directory_list = sorted(os.listdir(uploaded_file_directory))
        self.assertEqual(uploaded_file_directory_list, ["hello.c", "results.zip", "stdout.txt"],
            msg="Path {path} does not contain exactly 3 files: {entry_list}".format(
                path=uploaded_file_directory,
                entry_list=uploaded_file_directory_list
            )
        )

        self.assertTrue(filecmp.cmp(uploaded_file_directory + "/hello.c", self.c_source_code_snippet_hello_c))

        with ZipFile(file=uploaded_file_directory + "/results.zip", mode="r") as file_system_zip:
            self.assertIsNone(file_system_zip.testzip())
            self.assertEqual(file_system_zip.namelist(), ["stdout.txt"])
            file_system_zip_infolist = file_system_zip.infolist()
            self.assertEqual(os.stat(uploaded_file_directory + "/stdout.txt").st_size, file_system_zip_infolist[0].file_size)

            with ZipFile(response.response.file, 'r') as response_zip:
                self.assertIsNone(response_zip.testzip())
                self.assertEqual(response_zip.namelist(), ["stdout.txt"])
                response_zip_infolist = response_zip.infolist()

                self.assertEqual(file_system_zip_infolist[0].file_size, response_zip_infolist[0].file_size,
                    msg="STDOUT files do not have the same size inside the two zip files"
                )

        test_all_files = file_model.SourceCodeFile.get_all_files()
        self.assertEqual(test_all_files, [],
            msg="Files table in DB is not empty: {files}".format(
                files=test_all_files
            )
        )
