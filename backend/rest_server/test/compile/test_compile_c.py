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
        self.assertEqual(self.handler_c.root_upload_path, "/results/emscripten")
