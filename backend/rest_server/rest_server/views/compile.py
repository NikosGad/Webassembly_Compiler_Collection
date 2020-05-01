from flask import jsonify

from rest_server import app
from .. import authentication
from ..compile.compile import compile, compile_and_store_in_DB
from ..compile import compilation_handlers_dictionary

@app.route('/api/compile/<language>', methods=['POST'])
def perform_compilation(language):
    compilation_handler = compilation_handlers_dictionary.get(language)
    if not compilation_handler:
        return jsonify({"type": "LanguageNotSupportedError", "message": "Language {} is not supported.".format(language)}), 400

    return compile(compilation_handler.root_upload_path, compilation_handler.compilation_options_parser, compilation_handler.compilation_command_generator, compilation_handler.results_zip_appender)

@app.route('/api/compile/<language>/store', methods=['POST'])
@authentication.Authentication.authentication_required
def perform_compilation_and_store(language):
    compilation_handler = compilation_handlers_dictionary.get(language)
    if not compilation_handler:
        return jsonify({"type": "LanguageNotSupportedError", "message": "Language {} is not supported.".format(language)}), 400

    return compile_and_store_in_DB(compilation_handler.root_upload_path, compilation_handler.compilation_options_parser, compilation_handler.compilation_command_generator, compilation_handler.results_zip_appender)
