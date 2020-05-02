import datetime
import hashlib
from flask import jsonify

def debug_request(request):
    debug_message = '''
+=================+
REQUEST
{request}

HEADERS:
{request_headers}

FILES:
{request_files}

TEXT:
{request_text}

JSON:
{request_json}
-=================-\
'''.format(request=str(request), request_headers=str(request.headers), request_files=str(request.files), request_text=str(request.form), request_json=str(request.json))

    return debug_message

def log_in_username_password_incorrect():
    return jsonify({"type": "LogInError", "message": "Username, password or both are incorrect."}), 400

def generate_file_subpath(client_file):
    sha256_hash = hashlib.sha256()

    for byte_block in iter(lambda: client_file.read(4096),b""):
        sha256_hash.update(byte_block)

    # Rewind file pointer to the beginning
    client_file.seek(0)

    return str(datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S%f")) + "_" + sha256_hash.hexdigest()
