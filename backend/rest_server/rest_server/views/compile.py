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
        return compile(UPLOAD_PATH_EMSCRIPTEN, compile_c.parse_c_compilation_options, compile_c.generate_c_compile_command, compile_c.append_c_results_zip)
    else:
        return common.language_uri_mismatch()

@app.route('/compile_c_and_store', methods=['POST'])
@authentication.Authentication.authentication_required
def perform_c_compilation_and_store():
    if request.form["language"] == "C":
        return compile_and_store_in_DB(UPLOAD_PATH_EMSCRIPTEN, compile_c.parse_c_compilation_options, compile_c.generate_c_compile_command, compile_c.append_c_results_zip)
    else:
        return common.language_uri_mismatch()

@app.route('/compile_cpp', methods=['POST'])
def perform_cpp_compilation():
    if request.form["language"] == "C++":
        return compile(UPLOAD_PATH_EMSCRIPTEN, compile_cpp.parse_cpp_compilation_options, compile_cpp.generate_cpp_compile_command, compile_cpp.append_cpp_results_zip)
    else:
        return common.language_uri_mismatch()

@app.route('/compile_cpp_and_store', methods=['POST'])
@authentication.Authentication.authentication_required
def perform_cpp_compilation_and_store():
    if request.form["language"] == "C++":
        return compile_and_store_in_DB(UPLOAD_PATH_EMSCRIPTEN, compile_cpp.parse_cpp_compilation_options, compile_cpp.generate_cpp_compile_command, compile_cpp.append_cpp_results_zip)
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
