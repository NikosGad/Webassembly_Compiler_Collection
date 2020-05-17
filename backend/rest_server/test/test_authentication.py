import time
import unittest

from flask import g
from rest_server import app, authentication

# class AuthenticationEncodeDecodeFlowTestCase(object):
#     """Testsuite to test the generate and decode json web token."""
#     def test_authentication_generate_token(self):
#


class AuthenticationTestCase(unittest.TestCase):
    """Testsuite for authentication.py module."""
    @classmethod
    def setUpClass(cls):
        cls.token_valid = authentication.Authentication.generate_token(1, 60)
        cls.decoded_token_valid = 1
        cls.token_expired = authentication.Authentication.generate_token(2, 0, 0)
        cls.decoded_token_expired = "Token expired. Please Login again."
        cls.token_invalid = "one.invalid.token"
        cls.decoded_token_invalid = "Invalid Token. Please Login first."

    @classmethod
    def tearDownClass(cls):
        pass

    def dummy_function(self, dummy_parameter):
        return "Real parameter is {} but dummy_function always returns 42".format(dummy_parameter)

    def test_authentication_generate_token(self):
        token = authentication.Authentication.generate_token(1)

        self.assertIsInstance(token, str)
        self.assertEqual(len(token.split(".")), 3, msg="JWToken should have three parts separated by a dot.")

    def test_authentication_decode_token__valid_token(self):
        returned_decoded_token = authentication.Authentication.decode_token(self.token_valid)

        self.assertEqual(returned_decoded_token, self.decoded_token_valid)

    def test_authentication_decode_token__invalid_token(self):
        returned_decoded_token = authentication.Authentication.decode_token(self.token_invalid)

        self.assertEqual(returned_decoded_token, self.decoded_token_invalid)

    def test_authentication_decode_token__expired_token(self):
        # Sleep is needed to make sure that the token is expired.
        # The token is instantly expired thus 1 second is enough.
        time.sleep(1)
        returned_decoded_token = authentication.Authentication.decode_token(self.token_expired)

        self.assertEqual(returned_decoded_token, self.decoded_token_expired)

    def test_authentication_authentication_required__authorized(self):
        mock_request_authorization_valid_token = {
            "headers": {
                "Authorization": "Bearer " + self.token_valid
            },
        }

        with app.test_request_context(**mock_request_authorization_valid_token):
            result = authentication.Authentication.authentication_required(self.dummy_function)(1)

            self.assertEqual(result, "Real parameter is 1 but dummy_function always returns 42")
            self.assertEqual(g.user, {"id": self.decoded_token_valid})

    def test_authentication_authentication_required__authorization_header_missing(self):
        with app.test_request_context():
            response = authentication.Authentication.authentication_required(self.dummy_function)(1)

            self.assertEqual(response._status, "401 UNAUTHORIZED")
            self.assertEqual(response.headers.get("Content-Type"), "application/json")
            self.assertEqual(response.headers.get("WWW-Authenticate"), "Bearer realm=\"Access to user specific resources\"")
            self.assertEqual(response.response[0], b'{"message":"Authorization Header is missing","type":"AuthorizationViolation"}\n')

    def test_authentication_authentication_required__authorization_header_malformed(self):
        # TODO: Loop over some cases e.g.
        # Authorization: random1 random2,
        # Authorization: Bearer random,
        malformed_authorization_header_list = [
            "",
            self.token_valid,
            "random_string",
            "Bearer",
            "Bearer" + self.token_valid,
            "Bearer  ",
            "Bearer string_1 ",
            "Bearer string_1 string_2",
            "Bearer " + self.token_valid + " ",
            "Bearer " + self.token_valid + " " + self.token_valid,
            "Bearer Bearer Bearer",
        ]

        for malformed_authorization_header in malformed_authorization_header_list:
            mock_request = {
                "headers": {
                    "Authorization": malformed_authorization_header
                }
            }

            with app.test_request_context(**mock_request):
                response = authentication.Authentication.authentication_required(self.dummy_function)(1)

                self.assertEqual(response._status, "401 UNAUTHORIZED")
                self.assertEqual(response.headers.get("Content-Type"), "application/json")
                self.assertEqual(response.headers.get("WWW-Authenticate"), "Bearer realm=\"Access to user specific resources\"")
                self.assertEqual(response.response[0],
                    '{{"message":"Authorization Header {header} is incorrect","type":"AuthorizationViolation"}}\n'.format(
                        header=malformed_authorization_header
                    ).encode("utf-8")
                )

    def test_authentication_authentication_required__invalid_token(self):
        pass

    def test_authentication_authentication_required__expired_token(self):
        pass
