from flask import request

from rest_server import app
from rest_server import UPLOAD_PATH_EMSCRIPTEN, UPLOAD_PATH_GOLANG, ROOT_UPLOAD_PATHS
from .. import authentication
from .. import common
from ..compile.compile import compile, compile_and_store_in_DB
from ..compile import compile_c
from ..compile import compile_cpp
from ..compile import compile_golang

@app.route('/compile_c', methods=['POST'])
def perform_c_compilation():
    if request.form["language"] == "C":
        c_handler = compile_c.CCompilationHandler("C", UPLOAD_PATH_EMSCRIPTEN)
        app.logger.debug(c_handler)
        return compile(UPLOAD_PATH_EMSCRIPTEN, c_handler.compilation_options_parser, c_handler.compilation_command_generator, c_handler.results_zip_appender)
    else:
        return common.language_uri_mismatch()

@app.route('/compile_c_and_store', methods=['POST'])
@authentication.Authentication.authentication_required
def perform_c_compilation_and_store():
    if request.form["language"] == "C":
        c_handler = compile_c.CCompilationHandler("C", UPLOAD_PATH_EMSCRIPTEN)
        app.logger.debug(c_handler)
        return compile_and_store_in_DB(UPLOAD_PATH_EMSCRIPTEN, c_handler.compilation_options_parser, c_handler.compilation_command_generator, c_handler.results_zip_appender)
    else:
        return common.language_uri_mismatch()

@app.route('/compile_cpp', methods=['POST'])
def perform_cpp_compilation():
    if request.form["language"] == "C++":
        cpp_handler = compile_cpp.CppCompilationHandler("C++", UPLOAD_PATH_EMSCRIPTEN)
        app.logger.debug(cpp_handler)
        return compile(UPLOAD_PATH_EMSCRIPTEN, cpp_handler.compilation_options_parser, cpp_handler.compilation_command_generator, cpp_handler.results_zip_appender)
    else:
        return common.language_uri_mismatch()

@app.route('/compile_cpp_and_store', methods=['POST'])
@authentication.Authentication.authentication_required
def perform_cpp_compilation_and_store():
    if request.form["language"] == "C++":
        cpp_handler = compile_cpp.CppCompilationHandler("C++", UPLOAD_PATH_EMSCRIPTEN)
        app.logger.debug(cpp_handler)
        return compile_and_store_in_DB(UPLOAD_PATH_EMSCRIPTEN, cpp_handler.compilation_options_parser, cpp_handler.compilation_command_generator, cpp_handler.results_zip_appender)
    else:
        return common.language_uri_mismatch()

@app.route('/compile_golang', methods=['POST'])
def perform_golang_compilation():
    if request.form["language"] == "Golang":
        return compile(UPLOAD_PATH_GOLANG, compile_golang.parse_golang_compilation_options, compile_golang.generate_golang_compile_command, compile_golang.append_golang_results_zip)
    else:
        return common.language_uri_mismatch()

@app.route('/compile_golang_and_store', methods=['POST'])
@authentication.Authentication.authentication_required
def perform_golang_compilation_and_store():
    if request.form["language"] == "Golang":
        return compile_and_store_in_DB(UPLOAD_PATH_GOLANG, compile_golang.parse_golang_compilation_options, compile_golang.generate_golang_compile_command, compile_golang.append_golang_results_zip)
    else:
        return common.language_uri_mismatch()
