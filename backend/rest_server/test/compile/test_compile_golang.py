import errno
import os
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

from rest_server.compile import compile_golang

class CompileGolangTestCase(unittest.TestCase):
    """Testsuite for compile/compile_golang.py module."""
    @classmethod
    def setUpClass(cls):
        cls.handler_golang = compile_golang.GolangCompilationHandler()

        cls.test_working_directory = cls.handler_golang.root_upload_path
        cls.test_html_name = "test_output.html"
        cls.test_js_name = "test_output.js"
        cls.test_wasm_name = "test_output.wasm"
        cls.test_zip_name = "test_zip.zip"

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.test_working_directory + "/" + cls.test_html_name):
            os.remove(cls.test_working_directory + "/" + cls.test_html_name)

        if os.path.isfile(cls.test_working_directory + "/" + cls.test_wasm_name):
            os.remove(cls.test_working_directory + "/" + cls.test_wasm_name)

        if os.path.isfile(cls.test_working_directory + "/" + cls.test_zip_name):
            os.remove(cls.test_working_directory + "/" + cls.test_zip_name)

    def test_GolangCompilationHandler_init(self):
        self.assertEqual(self.handler_golang.language, "Golang")
        self.assertIsNotNone(self.handler_golang.root_upload_path)

    def test_GolangCompilationHandler_compilation_options_parser(self):
        kwargs_list = [
            {},
            {
                "output_filename": ""
            },
            {
                "optimization_level": True,
                "hack1": True,
                "hack2": False,
                "hack3": "hack",
                "iso_standard": "gnu++11",
                "suppress_warnings": "hack",
                "output_filename": "test_output.out"
            },
            {
                "output_filename": "../../bash.sh"
            },
            {
                "output_filename": ".././bash.sh"
            },
            {
                "output_filename": "../../.hidden_dir/.././bash.sh"
            },
            {
                "output_filename": "-g=ERROR"
            },
            {
                "output_filename": "-g++1"
            },
            {
                "output_filename": "-g--1"
            },
            {
                "output_filename": "-g*1"
            },
            {
                "output_filename": "-g:1"
            },
            {
                "output_filename": "rm -rf ../ /"
            },
            {
                "output_filename": "-----test -"
            },
            {
                "output_filename": "--- -"
            },
            {
                "output_filename": "----- "
            },
            {
                "output_filename": "-----"
            },
            {
                "output_filename": "../../.././../"
            },
        ]

        expected_results_list = [
            ([], "a.out"),
            ([], "a.out"),
            ([], "test_output.out"),
            ([], "bash.sh"),
            ([], "bash.sh"),
            ([], "hidden_dir_.._._bash.sh"),
            ([], "gERROR"),
            ([], "g1"),
            ([], "g--1"), # Dashes are allowed inside the file name
            ([], "g1"),
            ([], "g1"),
            ([], "rm_-rf"),
            ([], "test_-"),
            ([], "_-"),
            ([], "a.out"),
            ([], "a.out"),
            ([], "a.out"),
        ]

        self.assertEqual(len(kwargs_list), len(expected_results_list))

        for index, kwargs in enumerate(kwargs_list):
            result = self.handler_golang.compilation_options_parser(**kwargs)

            self.assertEqual(result, expected_results_list[index], msg=
                "Failure with kwargs: {kwargs_dict}".format(
                    kwargs_dict=kwargs
                )
            )

    def test_GolangCompilationHandler_compilation_command_generator(self):
        kwargs_list = [
            {
                "working_directory": "/path/to/upload/dir",
                "parsed_compilation_options": [],
                "input_filename": "input_filename.in",
                "output_filename": "output_filename"
            },
        ]

        expected_results_list = [
            ["go", "build", "-o", "/path/to/upload/dir/output_filename.wasm", "/path/to/upload/dir/input_filename.in"],
        ]

        for index, kwargs in enumerate(kwargs_list):
            result = self.handler_golang.compilation_command_generator(**kwargs)

            self.assertEqual(result, expected_results_list[index], msg=
                "Failure with kwargs: {kwargs_dict}".format(
                    kwargs_dict=kwargs
                )
            )

    def test_GolangCompilationHandler_results_zip_appender(self):
        test_compression = ZIP_DEFLATED
        test_compresslevel = 6

        with open(file=self.test_working_directory + "/" + self.test_wasm_name, mode="w"):
            pass

        if not os.path.isfile(self.test_working_directory + "/" + self.test_wasm_name):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.test_working_directory + "/" + self.test_wasm_name)

        with ZipFile(file=self.test_working_directory + "/" + self.test_zip_name, mode="w", compression=test_compression, compresslevel=test_compresslevel) as test_zip:
            self.assertEqual(test_zip.namelist(), [])

        if not os.path.isfile(self.test_working_directory + "/" + self.test_zip_name):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.test_working_directory + "/" + self.test_zip_name)

        result = self.handler_golang.results_zip_appender(
            working_directory=self.test_working_directory,
            results_zip_name=self.test_zip_name,
            output_filename="test_output",
            compression=test_compression,
            compresslevel=test_compresslevel)

        self.assertIsNone(result)

        with open(file=self.test_working_directory + "/" + self.test_html_name, mode="r") as html_file:
            for line_num, line in enumerate(html_file, 1):
                if line_num == 20:
                    line_20 = line

                if line_num == 31:
                    line_31 = line
                    break
            else:
                raise AssertionError("The file {file_name} contains less than 31 lines.".format(file_name=self.test_working_directory + "/" + self.test_html_name))

        self.assertEqual("\t<script src=\"test_output.js\"></script>\n", line_20)
        self.assertEqual("\t\tWebAssembly.instantiateStreaming(fetch(\"test_output.wasm\"), go.importObject).then((result) => {\n", line_31)

        with ZipFile(file=self.test_working_directory + "/" + self.test_zip_name, mode="r") as test_zip:
            self.assertEqual(test_zip.namelist(), [self.test_html_name, self.test_js_name, self.test_wasm_name])
