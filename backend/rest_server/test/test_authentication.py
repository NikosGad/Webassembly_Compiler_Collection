import time
import unittest

from rest_server import authentication

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
        pass

    def test_authentication_authentication_required__authorization_header_missing(self):
        pass

    def test_authentication_authentication_required__authorization_header_malformed(self):
        # TODO: Loop over some cases e.g.
        # Authorization: ,
        # Authorization: random,
        # Authorization: Bearer,
        # Authorization: Bearer<correct_jwt>,
        # Authorization: random1 random2,
        # Authorization: Bearer random,
        # Authorization: Bearer random1 random2
        pass

    def test_authentication_authentication_required__invalid_token(self):
        pass

    def test_authentication_authentication_required__expired_token(self):
        pass
