from flask import jsonify

from rest_server import app
from .. import authentication
from ..compile import compilation_handlers_dictionary

@app.route('/api/compile/<language>', methods=['POST'])
def perform_compilation(language):
    compilation_handler = compilation_handlers_dictionary.get(language)
    if not compilation_handler:
        return jsonify({"type": "LanguageNotSupportedError", "message": "Language {} is not supported.".format(language)}), 400

    return compilation_handler.compile()

@app.route('/api/compile/<language>/store', methods=['POST'])
@authentication.Authentication.authentication_required
def perform_compilation_and_store(language):
    compilation_handler = compilation_handlers_dictionary.get(language)
    if not compilation_handler:
        return jsonify({"type": "LanguageNotSupportedError", "message": "Language {} is not supported.".format(language)}), 400

    return compilation_handler.compile(store=True)
