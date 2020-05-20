import unittest

from rest_server.compile import compile_c

class CompileCTestCase(unittest.TestCase):
    """Testsuite for compile/compile_c.py module."""
    @classmethod
    def setUpClass(cls):
        cls.handler_c = compile_c.CCompilationHandler()

    @classmethod
    def tearDownClass(cls):
        pass

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
                "working_directory": "/path/to/upload/dir/",
                "parsed_compilation_options": [],
                "input_filename": "input_filename.in",
                "output_filename": "output_filename"
            },
            {
                "working_directory": "/path/to/upload/dir/",
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
        pass
