import datetime
import filecmp
import hashlib
import io
import os
import shutil
import unittest
from zipfile import ZipFile

from flask import g, request

from rest_server import app
from rest_server.compile.compile import CompilationHandler
from rest_server.models import user_model, file_model

CURRENT_TEST_FILE_PATH = os.path.dirname(__file__) + "/test_compile.py"

class NonAbstractCompilationHandler(CompilationHandler):
    """NonAbstractCompilationHandler class implements dummy methods for the abstract methods."""
    def compilation_options_parser(self, *args, **kwargs):
        return ["mock_option_1", "mock_option_2"], "mock_output_name"

    def compilation_command_generator(self, *args, **kwargs):
        return []

    def results_zip_appender(self, *args, **kwargs):
        pass

class MockedCompilationHandler(NonAbstractCompilationHandler):
    """MockedCompilationHandler class mocks up all the CompilationHandler methods except the compile method."""
    def _generate_file_subpath(self, client_file):
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
        os.makedirs(cls.mock_root_upload_path)
        cls.c_source_code_snippet_hello_c = os.path.dirname(__file__) + "/../test_source_code_snippets/hello.c"

        cls.user_info = {
            "username": "test_user_compile",
            "password": "12345a",
            "email": "test@mail.com"
        }

        cls.test_user = user_model.User(**cls.user_info)
        cls.test_user.id = cls.user_info["id"] = 1
        cls.test_user.create()

    @classmethod
    def tearDownClass(cls):
        cls.test_user.delete()

        if os.path.exists(cls.mock_root_upload_path):
            shutil.rmtree(cls.mock_root_upload_path)

        test_all_files = file_model.SourceCodeFile.get_all_files()
        for file in test_all_files:
            file.delete()

    def setUp(self):
        if os.path.exists(self.mock_root_upload_path) and os.listdir(self.mock_root_upload_path) != []:
            raise Exception("Path {path} is not empty before the testcase is executed: {entry_list}".format(
                    path=self.mock_root_upload_path,
                    entry_list=os.listdir(self.mock_root_upload_path),
                )
            )

        test_all_files = file_model.SourceCodeFile.get_all_files()
        if test_all_files != []:
            raise Exception("There are leftovers in sourcecodefiles table in DB")

    def tearDown(self):
        if os.path.exists(self.mock_root_upload_path):
            for entry in os.listdir(self.mock_root_upload_path):
                entry_path = self.mock_root_upload_path + "/" + entry
                if os.path.isdir(entry_path):
                    shutil.rmtree(entry_path)
                else:
                    os.remove(entry_path)

        test_all_files = file_model.SourceCodeFile.get_all_files()
        for file in test_all_files:
            file.delete()

    def test_CompilationHandler_generate_file_subpath(self):
        handler = NonAbstractCompilationHandler(self.mock_language, self.mock_root_upload_path)

        with open(self.c_source_code_snippet_hello_c, "rb") as test_file:
            result = handler._generate_file_subpath(test_file)

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
            '{"key": }',
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

        with open(uploaded_file_directory + "/stdout.txt", "r") as stdout_file:
            self.assertEqual(stdout_file.read(), CURRENT_TEST_FILE_PATH + "\n\n")

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
            msg="Table sourcecodefiles in DB is not empty: {files}".format(
                files=test_all_files
            )
        )

    def test_CompilationHandler_compile__with_stderr(self):
        handler = MockedCompilationHandlerWStderr(self.mock_language, self.mock_root_upload_path)

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

        self.assertEqual(response._status, "400 BAD REQUEST")
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
        self.assertEqual(uploaded_file_directory_list, ["hello.c", "results.zip", "stderr.txt"],
            msg="Path {path} does not contain exactly 3 files: {entry_list}".format(
                path=uploaded_file_directory,
                entry_list=uploaded_file_directory_list
            )
        )

        self.assertTrue(filecmp.cmp(uploaded_file_directory + "/hello.c", self.c_source_code_snippet_hello_c))

        with open(uploaded_file_directory + "/stderr.txt", "r") as stderr_file:
            self.assertEqual(stderr_file.read(), "ls: cannot access 'non-existing-path': No such file or directory\n\n")

        with ZipFile(file=uploaded_file_directory + "/results.zip", mode="r") as file_system_zip:
            self.assertIsNone(file_system_zip.testzip())
            self.assertEqual(file_system_zip.namelist(), ["stderr.txt"])
            file_system_zip_infolist = file_system_zip.infolist()
            self.assertEqual(os.stat(uploaded_file_directory + "/stderr.txt").st_size, file_system_zip_infolist[0].file_size)

            with ZipFile(response.response.file, 'r') as response_zip:
                self.assertIsNone(response_zip.testzip())
                self.assertEqual(response_zip.namelist(), ["stderr.txt"])
                response_zip_infolist = response_zip.infolist()

                self.assertEqual(file_system_zip_infolist[0].file_size, response_zip_infolist[0].file_size,
                    msg="STDERR files do not have the same size inside the two zip files"
                )

        test_all_files = file_model.SourceCodeFile.get_all_files()
        self.assertEqual(test_all_files, [],
            msg="Table sourcecodefiles in DB is not empty: {files}".format(
                files=test_all_files
            )
        )

    def test_CompilationHandler_compile__with_stdout_and_stderr(self):
        handler = MockedCompilationHandlerWStdoutWStderr(self.mock_language, self.mock_root_upload_path)

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

        self.assertEqual(response._status, "400 BAD REQUEST")
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
        self.assertEqual(uploaded_file_directory_list, ["hello.c", "results.zip", "stderr.txt", "stdout.txt"],
            msg="Path {path} does not contain exactly 4 files: {entry_list}".format(
                path=uploaded_file_directory,
                entry_list=uploaded_file_directory_list
            )
        )

        self.assertTrue(filecmp.cmp(uploaded_file_directory + "/hello.c", self.c_source_code_snippet_hello_c))

        with open(uploaded_file_directory + "/stdout.txt", "r") as stdout_file:
            self.assertEqual(stdout_file.read(), CURRENT_TEST_FILE_PATH + "\n\n")

        with open(uploaded_file_directory + "/stderr.txt", "r") as stderr_file:
            self.assertEqual(stderr_file.read(), "ls: cannot access 'non-existing-path': No such file or directory\n\n")

        with ZipFile(file=uploaded_file_directory + "/results.zip", mode="r") as file_system_zip:
            self.assertIsNone(file_system_zip.testzip())
            self.assertEqual(file_system_zip.namelist(), ["stdout.txt", "stderr.txt"])
            file_system_zip_infolist = file_system_zip.infolist()
            self.assertEqual(os.stat(uploaded_file_directory + "/stdout.txt").st_size, file_system_zip_infolist[0].file_size)
            self.assertEqual(os.stat(uploaded_file_directory + "/stderr.txt").st_size, file_system_zip_infolist[1].file_size)

            with ZipFile(response.response.file, 'r') as response_zip:
                self.assertIsNone(response_zip.testzip())
                self.assertEqual(response_zip.namelist(), ["stdout.txt", "stderr.txt"])
                response_zip_infolist = response_zip.infolist()

                self.assertEqual(file_system_zip_infolist[0].file_size, response_zip_infolist[0].file_size,
                    msg="STDOUT files do not have the same size inside the two zip files"
                )
                self.assertEqual(file_system_zip_infolist[1].file_size, response_zip_infolist[1].file_size,
                    msg="STDERR files do not have the same size inside the two zip files"
                )

        test_all_files = file_model.SourceCodeFile.get_all_files()
        self.assertEqual(test_all_files, [],
            msg="Table sourcecodefiles in DB is not empty: {files}".format(
                files=test_all_files
            )
        )

    def test_CompilationHandler_compile__store_successful_command(self):
        handler = MockedCompilationHandlerWStdout(self.mock_language, self.mock_root_upload_path)

        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/test/compile/method",
            "data": {
                "code": (self.c_source_code_snippet_hello_c, ".././-h../ello.c"),
                "compilation_options": '{}',
            },
        }

        with app.test_request_context(**mock_request):
            g.user = {"id": self.user_info["id"]}
            response = handler.compile(request.files["code"], request.form["compilation_options"], store=True)

        self.assertEqual(response._status, "200 OK")
        self.assertEqual(response.headers.get("Content-Type"), "application/zip")
        self.assertEqual(response.headers.get("Content-Disposition"), "attachment; filename=results.zip")

        root_upload_path_list = os.listdir(self.mock_root_upload_path)
        self.assertEqual(root_upload_path_list, [str(self.user_info["id"])],
            msg="Path {path} does not contain only the {user_id} folder: {root_upload_path_list}".format(
                path=self.mock_root_upload_path,
                user_id=self.user_info["id"],
                root_upload_path_list=root_upload_path_list
            )
        )

        user_directory = self.mock_root_upload_path + "/" + str(self.user_info["id"])
        user_directory_list = os.listdir(user_directory)
        self.assertEqual(user_directory_list, ["mock_subpath"],
            msg="Path {path} does not contain only the mock_subpath file directory: {entry_list}".format(
                path=user_directory,
                entry_list=user_directory_list
            )
        )

        uploaded_file_directory = user_directory + "/mock_subpath"
        uploaded_file_directory_list = sorted(os.listdir(uploaded_file_directory))
        self.assertEqual(uploaded_file_directory_list, ["-h.._ello.c", "results.zip", "stdout.txt"],
            msg="Path {path} does not contain exactly 3 files: {entry_list}".format(
                path=uploaded_file_directory,
                entry_list=uploaded_file_directory_list
            )
        )

        self.assertTrue(filecmp.cmp(uploaded_file_directory + "/-h.._ello.c", self.c_source_code_snippet_hello_c))

        with open(uploaded_file_directory + "/stdout.txt", "r") as stdout_file:
            self.assertEqual(stdout_file.read(), CURRENT_TEST_FILE_PATH + "\n\n")

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
        self.assertEqual(len(test_all_files), 1,
            msg="Table sourcecodefiles in DB does not contain exactly one file: {files}".format(
                files=test_all_files
            )
        )

        test_file = test_all_files[0]
        self.assertEqual(test_file.user_id, self.user_info["id"])
        self.assertEqual(test_file.name, "-h.._ello.c")
        self.assertEqual(test_file.directory, "mock_subpath")
        self.assertEqual(test_file.compilation_options, ["mock_option_1", "mock_option_2"])
        self.assertEqual(test_file.language, self.mock_language)
        self.assertEqual(test_file.status, "Successful")

    def test_CompilationHandler_compile__store_erroneous_command(self):
        handler = MockedCompilationHandlerWStderr(self.mock_language, self.mock_root_upload_path)

        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/test/compile/method",
            "data": {
                "code": (self.c_source_code_snippet_hello_c, ".././-h../ello.c"),
                "compilation_options": '{}',
            },
        }

        with app.test_request_context(**mock_request):
            g.user = {"id": self.user_info["id"]}
            response = handler.compile(request.files["code"], request.form["compilation_options"], store=True)

        self.assertEqual(response._status, "400 BAD REQUEST")
        self.assertEqual(response.headers.get("Content-Type"), "application/zip")
        self.assertEqual(response.headers.get("Content-Disposition"), "attachment; filename=results.zip")

        root_upload_path_list = os.listdir(self.mock_root_upload_path)
        self.assertEqual(root_upload_path_list, [str(self.user_info["id"])],
            msg="Path {path} does not contain only the {user_id} folder: {root_upload_path_list}".format(
                path=self.mock_root_upload_path,
                user_id=self.user_info["id"],
                root_upload_path_list=root_upload_path_list
            )
        )

        user_directory = self.mock_root_upload_path + "/" + str(self.user_info["id"])
        user_directory_list = os.listdir(user_directory)
        self.assertEqual(user_directory_list, ["mock_subpath"],
            msg="Path {path} does not contain only the mock_subpath file directory: {entry_list}".format(
                path=user_directory,
                entry_list=user_directory_list
            )
        )

        uploaded_file_directory = user_directory + "/mock_subpath"
        uploaded_file_directory_list = sorted(os.listdir(uploaded_file_directory))
        self.assertEqual(uploaded_file_directory_list, ["-h.._ello.c", "results.zip", "stderr.txt"],
            msg="Path {path} does not contain exactly 3 files: {entry_list}".format(
                path=uploaded_file_directory,
                entry_list=uploaded_file_directory_list
            )
        )

        self.assertTrue(filecmp.cmp(uploaded_file_directory + "/-h.._ello.c", self.c_source_code_snippet_hello_c))

        with open(uploaded_file_directory + "/stderr.txt", "r") as stderr_file:
            self.assertEqual(stderr_file.read(), "ls: cannot access 'non-existing-path': No such file or directory\n\n")

        with ZipFile(file=uploaded_file_directory + "/results.zip", mode="r") as file_system_zip:
            self.assertIsNone(file_system_zip.testzip())
            self.assertEqual(file_system_zip.namelist(), ["stderr.txt"])
            file_system_zip_infolist = file_system_zip.infolist()
            self.assertEqual(os.stat(uploaded_file_directory + "/stderr.txt").st_size, file_system_zip_infolist[0].file_size)

            with ZipFile(response.response.file, 'r') as response_zip:
                self.assertIsNone(response_zip.testzip())
                self.assertEqual(response_zip.namelist(), ["stderr.txt"])
                response_zip_infolist = response_zip.infolist()

                self.assertEqual(file_system_zip_infolist[0].file_size, response_zip_infolist[0].file_size,
                    msg="STDERR files do not have the same size inside the two zip files"
                )

        test_all_files = file_model.SourceCodeFile.get_all_files()
        self.assertEqual(len(test_all_files), 1,
            msg="Table sourcecodefiles in DB does not contain exactly one file: {files}".format(
                files=test_all_files
            )
        )

        test_file = test_all_files[0]
        self.assertEqual(test_file.user_id, self.user_info["id"])
        self.assertEqual(test_file.name, "-h.._ello.c")
        self.assertEqual(test_file.directory, "mock_subpath")
        self.assertEqual(test_file.compilation_options, ["mock_option_1", "mock_option_2"])
        self.assertEqual(test_file.language, self.mock_language)
        self.assertEqual(test_file.status, "Erroneous")

    def test_CompilationHandler_compile__unexpected_exception_handling_upload_path_created(self):
        handler = NonAbstractCompilationHandler(self.mock_language, self.mock_root_upload_path)

        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/test/compile/method",
            "data": {
                "code": (self.c_source_code_snippet_hello_c, ".././hello.c"),
                "compilation_options": '{}',
            },
        }

        with self.assertLogs(app.logger, level="INFO") as logs_list:
            with app.test_request_context(**mock_request):
                response, response_status = handler.compile(request.files["code"], request.form["compilation_options"])

        self.assertEqual(response_status, 500)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.response[0], b"{\"message\":\"Internal Unexpected Error\",\"type\":\"UnexpectedException\"}\n")

        root_upload_path_list = os.listdir(self.mock_root_upload_path)
        self.assertEqual(root_upload_path_list, ["unknown"],
            msg="Path {path} does not contain only the unknown folder: {root_upload_path_list}".format(
                path=self.mock_root_upload_path,
                root_upload_path_list=root_upload_path_list
            )
        )

        unknown_directory = self.mock_root_upload_path + "/unknown"
        unknown_directory_list = os.listdir(unknown_directory)
        self.assertEqual(unknown_directory_list, [],
            msg="Path {path} is not empty: {entry_list}".format(
                path=unknown_directory,
                entry_list=unknown_directory_list
            )
        )

        test_all_files = file_model.SourceCodeFile.get_all_files()
        self.assertEqual(test_all_files, [],
            msg="Table sourcecodefiles in DB is not empty: {files}".format(
                files=test_all_files
            )
        )

        self.assertEqual(len(logs_list.output), 4,
            msg="There are expected exactly 4 log messages: {logs_list}".format(
                logs_list=logs_list
            )
        )
        self.assertIn("ERROR:", logs_list.output[0])
        self.assertIn("Unexpected error occured during compile()", logs_list.output[0])
        self.assertIn("WARNING:", logs_list.output[1])
        self.assertIn("Asserting that no orphaned directory is created...", logs_list.output[1])
        self.assertIn("WARNING:", logs_list.output[2])
        self.assertIn("Detected orphaned directory:", logs_list.output[2])
        self.assertIn("INFO:", logs_list.output[3])
        self.assertIn("Orphaned directory deleted:", logs_list.output[3])

    def test_CompilationHandler_compile__unexpected_exception_handling_upload_path_undeclared(self):
        handler = NonAbstractCompilationHandler(self.mock_language, self.mock_root_upload_path)

        mock_request = {
            "base_url": "http://127.0.0.1:8080",
            "path": "/api/test/compile/method",
            "data": {
                "code": (self.c_source_code_snippet_hello_c, ".././hello.c"),
                "compilation_options": '{}',
            },
        }

        with self.assertLogs(app.logger, level="INFO") as logs_list:
            with app.test_request_context(**mock_request):
                response, response_status = handler.compile(request.files["code"], request.form["compilation_options"], store=True)

        self.assertEqual(response_status, 500)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.response[0], b"{\"message\":\"Internal Unexpected Error\",\"type\":\"UnexpectedException\"}\n")

        root_upload_path_list = os.listdir(self.mock_root_upload_path)
        self.assertEqual(root_upload_path_list, [],
            msg="Path {path} is not empty: {root_upload_path_list}".format(
                path=self.mock_root_upload_path,
                root_upload_path_list=root_upload_path_list
            )
        )

        test_all_files = file_model.SourceCodeFile.get_all_files()
        self.assertEqual(test_all_files, [],
            msg="Table sourcecodefiles in DB is not empty: {files}".format(
                files=test_all_files
            )
        )

        self.assertEqual(len(logs_list.output), 3,
            msg="There are expected exactly 3 log messages: {logs_list}".format(
                logs_list=logs_list
            )
        )
        self.assertIn("ERROR:", logs_list.output[0])
        self.assertIn("Unexpected error occured during compile()", logs_list.output[0])
        self.assertIn("WARNING:", logs_list.output[1])
        self.assertIn("Asserting that no orphaned directory is created...", logs_list.output[1])
        self.assertIn("INFO:", logs_list.output[2])
        self.assertIn("No orphaned directory is created", logs_list.output[2])
