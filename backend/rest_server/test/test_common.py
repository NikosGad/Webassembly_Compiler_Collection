import io
import unittest

from flask import request

from rest_server import app, common

class CommonTestCase(unittest.TestCase):
    """Testcase for the common.py module."""
    def test_debug_request(self):
        mock_request = {
            "base_url": "https://127.0.0.1:8080",
            "path": "/api/test/debug_message",
            "method": "POST",
            "headers": {
                "Origin": "http://localhost:3535"
            },
            "data": {
                "code": (io.BytesIO(b'this is some dummy test content'), 'test.txt'),
                "compilation_options": '{"optimization_level": "O2", "iso_standard": "gnu11", "suppress_warnings": true, "output_filename": "-----hello"}'
            },
        }
        with app.test_request_context(**mock_request):
            debug_request_msg = common.debug_request(request)

        self.assertIn("<Request 'https://127.0.0.1:8080/api/test/debug_message' [POST]>", debug_request_msg)
        self.assertIn("Host: 127.0.0.1:8080", debug_request_msg)
        self.assertIn("Content-Type: multipart/form-data; boundary=", debug_request_msg)
        self.assertIn("Origin: http://localhost:3535", debug_request_msg)
        self.assertIn("ImmutableMultiDict([('code', <FileStorage: 'test.txt' ('text/plain')>)])", debug_request_msg)
        self.assertIn("ImmutableMultiDict([('compilation_options', '{\"optimization_level\": \"O2\", \"iso_standard\": \"gnu11\", \"suppress_warnings\": true, \"output_filename\": \"-----hello\"}')])", debug_request_msg)
        self.assertIn("None", debug_request_msg)

    def test_log_in_username_password_incorrect(self):
        with app.app_context():
            response, response_status = common.log_in_username_password_incorrect()

        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.response[0], b'{"message":"Username, password or both are incorrect.","type":"LogInError"}\n')
        self.assertEqual(response_status, 400)
