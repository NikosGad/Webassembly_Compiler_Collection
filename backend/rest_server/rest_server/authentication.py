import datetime
import jwt
import os

JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY", "error_jwt_key")

class Authentication():
    @staticmethod
    def generate_token(user_id):
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
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
        except jwt.InvalidSignatureError:
            return "Invalid Token. Please Login first."
        except Exception:
            return "Error During Token Decode"
