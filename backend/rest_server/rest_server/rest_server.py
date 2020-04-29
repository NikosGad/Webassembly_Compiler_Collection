from rest_server import app
from rest_server import db
from rest_server import UPLOAD_PATH_EMSCRIPTEN, UPLOAD_PATH_GOLANG, ROOT_UPLOAD_PATHS
import json
import os
import subprocess
from flask import g, jsonify, request, send_from_directory, make_response
from marshmallow import ValidationError
from werkzeug.utils import secure_filename
from zipfile import ZipFile, ZIP_DEFLATED

from . import authentication
from .models import user_model
from .models import file_model

from . import common
from . import compile_c
from . import compile_cpp
from . import compile_golang

RESULTS_ZIP_NAME="results.zip"
COMPRESSION=ZIP_DEFLATED
COMPRESSLEVEL=6

user_schema = user_model.UserSchema()
file_schema = file_model.SourceCodeFileSchema()

def compile(language_root_upload_path, parser, command_generator, results_zip_appender):
    app.logger.debug(common.debug_request(request))

    client_file = request.files["mycode"]
    filename = secure_filename(client_file.filename)

    app.logger.debug("File information: " + str(client_file))
    app.logger.debug("Secure Filename: " + filename)
    app.logger.debug("Content-type: " + client_file.content_type)

    upload_path = language_root_upload_path + common.generate_file_subpath(client_file)
    try:
        os.makedirs(upload_path)
        app.logger.debug("Path generated: " + upload_path)
    except FileExistsError:
        app.logger.debug("Path exists: " + upload_path)

    try:
        compilation_options_json = json.loads(request.form["compilation_options"])
    except Exception:
        app.logger.exception("An error occured while loading compilation options json")
        return jsonify({"type": "JSONParseError", "message": "Bad JSON Format Error"}), 400

    compile_command, secured_output_filename = parser(**compilation_options_json)
    app.logger.debug("Parsed compile command: " + str(compile_command))
    app.logger.debug("Parsed Output Filename: " + secured_output_filename)

    compile_command = command_generator(upload_path, compile_command, filename, secured_output_filename)
    app.logger.debug("Final compile command: " + str(compile_command))

    subprocess.run(["ls", "-la", upload_path])

    try:
        client_file.save(upload_path + filename)
    except Exception:
        app.logger.exception("An error occured while saving: {filename}". format(filename=filename))
        return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500

    try:
        # DONT USE shell=True for security and vulnerabilities
        completed_compile_file_process = subprocess.run(compile_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if completed_compile_file_process.stdout:
            with open(upload_path + "stdout.txt", "w") as f_out:
                print(completed_compile_file_process.stdout.decode(encoding="utf-8"), file=f_out)

        if completed_compile_file_process.stderr:
            with open(upload_path + "stderr.txt", "w") as f_err:
                print(completed_compile_file_process.stderr.decode(encoding="utf-8"), file=f_err)

    except Exception:
        subprocess.run(["ls", "-la", upload_path])
        app.logger.exception("An error occured during: subprocess.run({compile_command})".format(compile_command=compile_command))
        return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500

    app.logger.debug("Compilation return code: " + str(completed_compile_file_process.returncode))

    with ZipFile(file=upload_path + RESULTS_ZIP_NAME, mode="w", compression=COMPRESSION, compresslevel=COMPRESSLEVEL) as results_zip:
        if completed_compile_file_process.stdout:
            results_zip.write(upload_path + "stdout.txt", "stdout.txt")

        if completed_compile_file_process.stderr:
            results_zip.write(upload_path + "stderr.txt", "stderr.txt")

    # TODO: Activate X-Sendfile
    if completed_compile_file_process.returncode == 0:
        return_status_code = 200
        results_zip_appender(upload_path, RESULTS_ZIP_NAME, secured_output_filename, "a", COMPRESSION, COMPRESSLEVEL)
    else:
        return_status_code = 400

    response = make_response(send_from_directory(upload_path, RESULTS_ZIP_NAME, as_attachment=True), return_status_code)
    response.headers["Content-Type"] = "application/zip"
    app.logger.debug(response.headers)
    app.logger.debug(response.__dict__)
    app.logger.debug(response.response.__dict__)
    subprocess.run(["ls", "-la", upload_path])
    return response

def compile_and_store_in_DB(language_root_upload_path, parser, command_generator, results_zip_appender):
    app.logger.debug(common.debug_request(request))

    client_file = request.files["mycode"]
    filename = secure_filename(client_file.filename)

    app.logger.debug("File information: " + str(client_file))
    app.logger.debug("Secure Filename: " + filename)
    app.logger.debug("Content-type: " + client_file.content_type)

    subpath = common.generate_file_subpath(client_file)[:-1]

    upload_path = language_root_upload_path + str(g.user["id"]) + "/" + subpath + "/"
    try:
        os.makedirs(upload_path)
        app.logger.debug("Path generated: " + upload_path)
    except FileExistsError:
        app.logger.debug("Path exists: " + upload_path)

    try:
        compilation_options_json = json.loads(request.form["compilation_options"])
    except Exception:
        app.logger.exception("An error occured while loading compilation options json")
        return jsonify({"type": "JSONParseError", "message": "Bad JSON Format Error"}), 400

    compile_command, secured_output_filename = parser(**compilation_options_json)
    app.logger.debug("Parsed compile command: " + str(compile_command))
    app.logger.debug("Parsed Output Filename: " + secured_output_filename)

    file_dictionary = {
    "user_id": g.user["id"],
    "name": filename,
    "directory":subpath,
    "compilation_options": compile_command,
    "language": request.form["language"],
    }

    compile_command = command_generator(upload_path, compile_command, filename, secured_output_filename)
    app.logger.debug("Final compile command: " + str(compile_command))

    subprocess.run(["ls", "-la", upload_path])

    try:
        client_file.save(upload_path + filename)
    except Exception:
        app.logger.exception("An error occured while saving: {filename}". format(filename=filename))
        return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500

    try:
        # DONT USE shell=True for security and vulnerabilities
        completed_compile_file_process = subprocess.run(compile_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if completed_compile_file_process.stdout:
            with open(upload_path + "stdout.txt", "w") as f_out:
                print(completed_compile_file_process.stdout.decode(encoding="utf-8"), file=f_out)

        if completed_compile_file_process.stderr:
            with open(upload_path + "stderr.txt", "w") as f_err:
                print(completed_compile_file_process.stderr.decode(encoding="utf-8"), file=f_err)

    except Exception:
        subprocess.run(["ls", "-la", upload_path])
        app.logger.exception("An error occured during: subprocess.run({compile_command})".format(compile_command=compile_command))
        return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500

    app.logger.debug("Compilation return code: " + str(completed_compile_file_process.returncode))

    with ZipFile(file=upload_path + RESULTS_ZIP_NAME, mode="w", compression=COMPRESSION, compresslevel=COMPRESSLEVEL) as results_zip:
        if completed_compile_file_process.stdout:
            results_zip.write(upload_path + "stdout.txt", "stdout.txt")

        if completed_compile_file_process.stderr:
            results_zip.write(upload_path + "stderr.txt", "stderr.txt")

    # TODO: Activate X-Sendfile
    if completed_compile_file_process.returncode == 0:
        return_status_code = 200
        file_dictionary["status"] = "Successful"
        results_zip_appender(upload_path, RESULTS_ZIP_NAME, secured_output_filename, "a", COMPRESSION, COMPRESSLEVEL)
    else:
        file_dictionary["status"] = "Erroneous"
        return_status_code = 400

    try:
        file_db = file_model.SourceCodeFile(**file_dictionary)
        file_db.create()
    except Exception:
        app.logger.exception("An error occured during: file_db.create()")
        return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500

    response = make_response(send_from_directory(upload_path, RESULTS_ZIP_NAME, as_attachment=True), return_status_code)
    response.headers["Content-Type"] = "application/zip"
    app.logger.debug(response.headers)
    app.logger.debug(response.__dict__)
    app.logger.debug(response.response.__dict__)
    subprocess.run(["ls", "-la", upload_path])
    return response

############ API ############
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


######### HTML #########
@app.route('/', methods=['GET'])
def show_index():
    # return render_template('./home.html')
    return "<h1 style='color:red'>Hello<h1 style='color:yellow'> flask and world</h1>"
