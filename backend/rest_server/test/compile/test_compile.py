import datetime
import hashlib
import os
import unittest

from rest_server.compile.compile import CompilationHandler

class NonAbstractCompilationHandler(CompilationHandler):
    """NonAbstractCompilationHandler class inherits from CompilationHandler in order to test subpath creation."""
    def compilation_options_parser(self, *args, **kwargs):
        pass

    def compilation_command_generator(self, *args, **kwargs):
        pass

    def results_zip_appender(self, *args, **kwargs):
        pass

class MockedCompilationHandler(NonAbstractCompilationHandler):
    """MockedCompilationHandler class mocks up all the CompilationHandler methods except the compile method."""
    def generate_file_subpath(self, client_file):
        return "mocked_subpath"

class CompileTestCase(unittest.TestCase):
    """Testsuite for compile/compile.py module."""
    # def setUp(self):
    #     self.test_file_path = os.path.dirname(__file__) + "/../test_source_code_snippets/hello.c"

    def test_compilation_handler_generate_file_subpath(self):
        handler = NonAbstractCompilationHandler("language", "/results/language")
        test_file_path = os.path.dirname(__file__) + "/../test_source_code_snippets/hello.c"

        with open(test_file_path, "rb") as test_file:
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
