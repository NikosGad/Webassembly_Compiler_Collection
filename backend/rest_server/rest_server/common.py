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

def language_uri_mismatch():
    return jsonify({"type": "LanguageSelectionError", "message": "Selected language does not match with the requested compile URI"}), 400

def log_in_username_password_incorrect():
    return jsonify({"type": "LogInError", "message": "Username, password or both are incorrect."}), 400
