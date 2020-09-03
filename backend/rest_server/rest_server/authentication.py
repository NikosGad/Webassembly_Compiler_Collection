from rest_server import app
import datetime
import functools
import jwt
import os
from flask import g, jsonify, make_response, request

JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY", "error_jwt_key")

class Authentication():
    @staticmethod
    def generate_token(user_id, minutes=120, seconds=0):
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=minutes, seconds=seconds),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            JWT_SECRET_KEY,
            algorithm='HS256'
        ).decode("utf-8")

    @staticmethod
    def decode_token(token):
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY)
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            return "Token expired. Please Login again."
        except (
            jwt.exceptions.InvalidTokenError,
            jwt.exceptions.DecodeError,
            jwt.exceptions.InvalidSignatureError,
            jwt.exceptions.ExpiredSignatureError,
            jwt.exceptions.InvalidAudienceError,
            jwt.exceptions.InvalidIssuerError,
            jwt.exceptions.InvalidIssuedAtError,
            jwt.exceptions.ImmatureSignatureError,
            jwt.exceptions.InvalidKeyError,
            jwt.exceptions.InvalidAlgorithmError,
            jwt.exceptions.MissingRequiredClaimError):
            return "Invalid Token. Please Login first."

    @staticmethod
    def authentication_required(func):
        @functools.wraps(func)
        def wrapper_authentication_required(*args, **kwargs):
            if "Authorization" not in request.headers:
                app.logger.debug("Authorization Header is missing")
                response = make_response(jsonify({"type": "AuthorizationViolation", "message": "Authorization Header is missing"}), 401)

                response.headers["WWW-Authenticate"] = "Bearer realm=\"Access to user specific resources\""
                response.headers["Content-Type"] = "application/json"
                return response

            authorization_header = request.headers["Authorization"]
            app.logger.debug("Authorization Header is: " + str(authorization_header))

            try:
                authorization_schema, authorization_jwt = authorization_header.split(" ")
            except Exception:
                app.logger.debug("Authorization Header is incorrect")
                response = make_response(jsonify({"type": "AuthorizationViolation", "message": "Authorization Header {} is incorrect".format(authorization_header)}), 401)

                response.headers["WWW-Authenticate"] = "Bearer realm=\"Access to user specific resources\""
                response.headers["Content-Type"] = "application/json"
                return response

            if authorization_schema != "Bearer":
                app.logger.debug("Authorization Schema is incorrect")
                response = make_response(jsonify({"type": "AuthorizationSchemaViolation", "message": "Authorization Schema {} is incorrect".format(authorization_schema)}), 401)

                response.headers["WWW-Authenticate"] = "Bearer realm=\"Access to user specific resources\""
                response.headers["Content-Type"] = "application/json"
                return response

            try:
                payload = Authentication.decode_token(authorization_jwt)
            except Exception: # pragma: no cover
                app.logger.exception("Error During Token Decode: " + authorization_jwt)
                response = make_response(jsonify({"type": "AuthorizationJWTViolation", "message": "Error During Token Decode"}), 401)

                response.headers["WWW-Authenticate"] = "Bearer realm=\"Access to user specific resources\""
                response.headers["Content-Type"] = "application/json"
                return response

            # If the payload is a string then the token is expired or invalid
            if type(payload) == str:
                app.logger.debug("JWT Decode result is: " + str(payload))
                response = make_response(jsonify({"type": "AuthorizationJWTViolation", "message": payload}), 401)

                response.headers["WWW-Authenticate"] = "Bearer realm=\"Access to user specific resources\""
                response.headers["Content-Type"] = "application/json"
                return response

            app.logger.debug("JWT Decoded Payload is: " + str(payload))
            g.user = {"id": payload}

            return func(*args, **kwargs)
        return wrapper_authentication_required
