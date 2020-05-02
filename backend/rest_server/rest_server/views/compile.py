from flask import jsonify, request

from rest_server import app
from .. import authentication
from .. import common
from ..compile import compilation_handlers_dictionary

@app.route('/api/compile/<language>', methods=['POST'])
def perform_compilation(language):
    app.logger.debug(common.debug_request(request))

    compilation_handler = compilation_handlers_dictionary.get(language)
    if not compilation_handler:
        return jsonify({"type": "LanguageNotSupportedError", "message": "Language {} is not supported.".format(language)}), 400

    source_code_file = request.files.get("mycode")
    compilation_options_json = request.form.get("compilation_options")
    if not source_code_file or not compilation_options_json:
        return jsonify({"type": "IncorrectCompileBodyError", "message": "A form data should be provided that contains a file with key 'code' and a compilation options json with key 'compilation_options'."}), 400

    return compilation_handler.compile()

@app.route('/api/compile/<language>/store', methods=['POST'])
@authentication.Authentication.authentication_required
def perform_compilation_and_store(language):
    app.logger.debug(common.debug_request(request))

    compilation_handler = compilation_handlers_dictionary.get(language)
    if not compilation_handler:
        return jsonify({"type": "LanguageNotSupportedError", "message": "Language {} is not supported.".format(language)}), 400

    source_code_file = request.files.get("mycode")
    compilation_options_json = request.form.get("compilation_options")
    if not source_code_file or not compilation_options_json:
        return jsonify({"type": "IncorrectCompileBodyError", "message": "A form data should be provided that contains a file with key 'code' and a compilation options json with key 'compilation_options'."}), 400

    return compilation_handler.compile(store=True)
