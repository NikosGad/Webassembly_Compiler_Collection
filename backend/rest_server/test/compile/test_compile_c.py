import errno
import os
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

from rest_server.compile import compile_c

class CompileCTestCase(unittest.TestCase):
    """Testsuite for compile/compile_c.py module."""
    @classmethod
    def setUpClass(cls):
        cls.handler_c = compile_c.CCompilationHandler()

        cls.test_working_directory = cls.handler_c.root_upload_path
        cls.test_html_name = "test_output.html"
        cls.test_js_name = "test_output.js"
        cls.test_wasm_name = "test_output.wasm"
        cls.test_zip_name = "test_zip.zip"

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.test_working_directory + "/" + cls.test_html_name):
            os.remove(cls.test_working_directory + "/" + cls.test_html_name)

        if os.path.isfile(cls.test_working_directory + "/" + cls.test_js_name):
            os.remove(cls.test_working_directory + "/" + cls.test_js_name)

        if os.path.isfile(cls.test_working_directory + "/" + cls.test_wasm_name):
            os.remove(cls.test_working_directory + "/" + cls.test_wasm_name)

        if os.path.isfile(cls.test_working_directory + "/" + cls.test_zip_name):
            os.remove(cls.test_working_directory + "/" + cls.test_zip_name)

    def test_CCompilationHandler_init(self):
        self.assertEqual(self.handler_c.language, "C")
        self.assertIsNotNone(self.handler_c.root_upload_path)

    def test_CCompilationHandler_compilation_options_parser(self):
        kwargs_list = [
            {},
            {
                "optimization_level": "O0",
                "iso_standard": "c89",
                "suppress_warnings": True,
                "output_filename": "test_output.out"
            },
            {
                "optimization_level": "O1",
                "iso_standard": "c90",
                "suppress_warnings": False,
                "output_filename": ""
            },
            {
                "optimization_level": "O2",
                "iso_standard": "c99",
            },
            {
                "optimization_level": "O3",
                "iso_standard": "c11",
            },
            {
                "optimization_level": "Os",
                "iso_standard": "c17",
            },
            {
                "optimization_level": "Oz",
                "iso_standard": "gnu89",
            },
            {
                "iso_standard": "gnu90",
            },
            {
                "iso_standard": "gnu99",
            },
            {
                "iso_standard": "gnu11",
            },
            {
                "iso_standard": "gnu17",
            },
            {
                "optimization_level": "-O2",
                "iso_standard": "-std=gnu17",
                "suppress_warnings": "True",
                "output_filename": ""
            },
            {
                "optimization_level": True,
                "hack1": True,
                "hack2": False,
                "hack3": "hack",
                "iso_standard": "gnu++11",
                "suppress_warnings": "hack",
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
            (["-O0", "-std=c89", "-w"], "test_output.out"),
            (["-O1", "-std=c90"], "a.out"),
            (["-O2", "-std=c99"], "a.out"),
            (["-O3", "-std=c11"], "a.out"),
            (["-Os", "-std=c17"], "a.out"),
            (["-Oz", "-std=gnu89"], "a.out"),
            (["-std=gnu90"], "a.out"),
            (["-std=gnu99"], "a.out"),
            (["-std=gnu11"], "a.out"),
            (["-std=gnu17"], "a.out"),
            ([], "a.out"),
            ([], "a.out"),
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

        for index, kwargs in enumerate(kwargs_list):
            result = self.handler_c.compilation_options_parser(**kwargs)

            self.assertEqual(result, expected_results_list[index], msg=
                "Failure with kwargs: {kwargs_dict}".format(
                    kwargs_dict=kwargs
                )
            )

    def test_CCompilationHandler_compilation_command_generator(self):
        kwargs_list = [
            {
                "working_directory": "/path/to/upload/dir",
                "parsed_compilation_options": [],
                "input_filename": "input_filename.in",
                "output_filename": "output_filename"
            },
            {
                "working_directory": "/path/to/upload/dir",
                "parsed_compilation_options": ["-O0", "-std=c89", "-w"],
                "input_filename": "input_filename.in",
                "output_filename": "a.out"
            },
        ]

        expected_results_list = [
            ["emcc", "-o", "/path/to/upload/dir/output_filename.html", "/path/to/upload/dir/input_filename.in"],
            ["emcc", "-O0", "-std=c89", "-w", "-o", "/path/to/upload/dir/a.out.html", "/path/to/upload/dir/input_filename.in"],
        ]

        for index, kwargs in enumerate(kwargs_list):
            result = self.handler_c.compilation_command_generator(**kwargs)

            self.assertEqual(result, expected_results_list[index], msg=
                "Failure with kwargs: {kwargs_dict}".format(
                    kwargs_dict=kwargs
                )
            )

    def test_CCompilationHandler_results_zip_appender(self):
        test_compression = ZIP_DEFLATED
        test_compresslevel = 6

        with open(file=self.test_working_directory + "/" + self.test_html_name, mode="w"):
            pass

        if not os.path.isfile(self.test_working_directory + "/" + self.test_html_name):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.test_working_directory + "/" + self.test_html_name)

        with open(file=self.test_working_directory + "/" + self.test_js_name, mode="w"):
            pass

        if not os.path.isfile(self.test_working_directory + "/" + self.test_js_name):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.test_working_directory + "/" + self.test_js_name)

        with open(file=self.test_working_directory + "/" + self.test_wasm_name, mode="w"):
            pass

        if not os.path.isfile(self.test_working_directory + "/" + self.test_wasm_name):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.test_working_directory + "/" + self.test_wasm_name)

        with ZipFile(file=self.test_working_directory + "/" + self.test_zip_name, mode="w", compression=test_compression, compresslevel=test_compresslevel) as test_zip:
            self.assertEqual(test_zip.namelist(), [])

        if not os.path.isfile(self.test_working_directory + "/" + self.test_zip_name):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.test_working_directory + "/" + self.test_zip_name)

        result = self.handler_c.results_zip_appender(
            working_directory=self.test_working_directory,
            results_zip_name=self.test_zip_name,
            output_filename="test_output",
            compression=test_compression,
            compresslevel=test_compresslevel)

        self.assertIsNone(result)

        with ZipFile(file=self.test_working_directory + "/" + self.test_zip_name, mode="r") as test_zip:
            self.assertEqual(test_zip.namelist(), [self.test_html_name, self.test_js_name, self.test_wasm_name])
