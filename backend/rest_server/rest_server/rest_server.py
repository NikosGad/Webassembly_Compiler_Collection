from rest_server import app
from rest_server import db
import json
import logging
import os
import socket
import subprocess
from flask import jsonify, request, send_from_directory, make_response
from marshmallow import ValidationError
from werkzeug.utils import secure_filename
from zipfile import ZipFile, ZIP_DEFLATED

from . import authentication
from . import models

from . import common
from . import compile_c
from . import compile_cpp
from . import compile_golang
#from flask_cors import CORS

RESULTS_ZIP_NAME="results.zip"
COMPRESSION=ZIP_DEFLATED
COMPRESSLEVEL=6
#CORS(app)
user_schema = models.UserSchema()

def compile(upload_path, parser, command_generator, results_zip_appender):
    app.logger.debug(common.debug_request(request))

    client_file = request.files["mycode"]
    filename = secure_filename(client_file.filename)

    app.logger.debug("File information: " + str(client_file))
    app.logger.debug("Secure Filename: " + filename)
    app.logger.debug("Content-type: " + client_file.content_type)

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
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3535"
    response.headers["Content-Type"] = "application/zip"
    app.logger.debug(response.headers)
    app.logger.debug(response.__dict__)
    app.logger.debug(response.response.__dict__)
    subprocess.run(["ls", "-la", upload_path])
    return response

UPLOAD_PATH_EMSCRIPTEN=os.environ.get("UPLOAD_PATH_EMSCRIPTEN", "/results/emscripten/")
UPLOAD_PATH_GOLANG=os.environ.get("UPLOAD_PATH_GOLANG", "/results/go/src/")

############ API ############
@app.route('/compile_c', methods=['POST'])
def perform_c_compilation():
    if request.form["language"] == "C":
        return compile(UPLOAD_PATH_EMSCRIPTEN, compile_c.parse_c_compilation_options, compile_c.generate_c_compile_command, compile_c.append_c_results_zip)
    else:
        return common.language_uri_mismatch()

@app.route('/compile_cpp', methods=['POST'])
def perform_cpp_compilation():
    if request.form["language"] == "C++":
        return compile(UPLOAD_PATH_EMSCRIPTEN, compile_cpp.parse_cpp_compilation_options, compile_cpp.generate_cpp_compile_command, compile_cpp.append_cpp_results_zip)
    else:
        return common.language_uri_mismatch()

@app.route('/compile_golang', methods=['POST'])
def perform_golang_compilation():
    if request.form["language"] == "Golang":
        return compile(UPLOAD_PATH_GOLANG, compile_golang.parse_golang_compilation_options, compile_golang.generate_golang_compile_command, compile_golang.append_golang_results_zip)
    else:
        return common.language_uri_mismatch()

@app.route('/api/signup', methods=['POST'])
def signup():
    app.logger.debug("Incoming Sign Up Request")
    sign_up_form = request.form
    app.logger.debug("User Data Form: " + str(sign_up_form))

    try:
        valid_sign_up_form = user_schema.load(sign_up_form)
    except ValidationError as e:
        app.logger.debug(e.messages)
        return jsonify({"type": "SignUpError", "message": e.messages}), 400, {"Access-Control-Allow-Origin": "http://localhost:3535"}

    app.logger.debug("Valid Sign Up Form: " + str(valid_sign_up_form))

    user_exists = models.User.get_user_by_username(valid_sign_up_form["username"])
    if user_exists:
        app.logger.debug("Username {} already exists".format(valid_sign_up_form["username"]))
        return jsonify({"type": "UniqueUsernameViolation", "message": "Username {} already exists".format(valid_sign_up_form["username"])}), 400, {"Access-Control-Allow-Origin": "http://localhost:3535"}

    user_exists = models.User.get_user_by_email(valid_sign_up_form["email"])
    if user_exists:
        app.logger.debug("Email {} already exists".format(valid_sign_up_form["email"]))
        return jsonify({"type": "UniqueEmailViolation", "message": "Email {} already exists".format(valid_sign_up_form["email"])}), 400, {"Access-Control-Allow-Origin": "http://localhost:3535"}

    try:
        user = models.User(**valid_sign_up_form)
        user.create()
    except Exception:
        app.logger.exception("An error occured during: user.create()")
        return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500

    return jsonify({"message": "OK"}), 200, {"Access-Control-Allow-Origin": "http://localhost:3535"}

@app.route('/api/login', methods=['POST'])
def login():
    app.logger.debug("Incoming Log In Request")
    log_in_form = request.form
    app.logger.debug("User Log In Data Form: " + str(log_in_form))

    if not log_in_form.get("username") or not log_in_form.get("password"):
        error_msg = "Both username and password are required to log in."
        app.logger.debug(error_msg)
        return jsonify({"type": "LogInError", "message": error_msg}), 400, {"Access-Control-Allow-Origin": "http://localhost:3535"}

    user = models.User.get_user_by_username(log_in_form["username"])

    if not user:
        app.logger.debug("Username {} is not a valid username".format(log_in_form["username"]))
        return common.log_in_username_password_incorrect()

    if not user.validate_password(log_in_form["password"]):
        app.logger.debug("Password {} is not valid for user {}".format(log_in_form["password"], log_in_form["username"]))
        return common.log_in_username_password_incorrect()

    app.logger.debug("Logged In User: " + str(user))
    try:
        token = authentication.Authentication.generate_token(user.id)
    except Exception as e:
        app.logger.exception("Error During Token Generation")
        return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500

    app.logger.debug("The generated token is: " + str(token))

    return jsonify({"message": "OK", "jwt": token}), 200, {"Access-Control-Allow-Origin": "http://localhost:3535"}

@app.route('/api/priv', methods=['POST'])
@authentication.Authentication.authentication_required
def priv_action():
    return jsonify({"message": "OK"}), 200, {"Access-Control-Allow-Origin": "http://localhost:3535"}

@app.route('/api/healthcheck', methods=['GET'])
def healthcheck():
    host_port_tuple_list = [('wasmcc', 8080), ('ucrm_db', 5432), ('nginx', 4200)]
    err = 0

    proxies = [('nginx', 4200)]
    proxies_amount = len(proxies)
    servers = [('wasmcc', 8080)]
    servers_amount = len(servers)
    databases = [('ucrm_db', 5432)]
    databases_amount = len(databases)

    graph = {
        "nodes": [
            {"id": "n0", "label": "wasmcc:8080", "container": "wasmcc", "port": 8080, "x": 0, "y": 0, "size": 1, "color": '#008cc2'},
            {"id": "n1", "label": "ucrm_db:5432", "container": "ucrm_db", "port": 5432, "x": 3, "y": 1, "size": 1, "color": '#008cc2'},
            {"id": "n2", "label": "nginx:4200", "container": "nginx", "port": 4200, "x": 1, "y": 1, "size": 1, "color": '#008cc2'},
        ]
    }
    graph1 = {"nodes": [], "edges": []}
    container_list = []

    for index, tuple in enumerate(proxies):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        app.logger.debug("Checking service:" + str(tuple))
        try:
            s.connect(tuple)
            s.close()
            app.logger.debug("\tConnected to " + str(tuple[0]))
            graph1["nodes"].append({"id": str(index), "label": tuple[0] + ":" + str(tuple[1]), "container": tuple[0], "port": tuple[1], "x": 0, "y": index, "size": 1, "color": "#008cc2"})
        except socket.error as ex:
            app.logger.debug("\tConnection failed with errno {0}: {1}\n\tWaiting for".format(ex.errno, ex.strerror) + str(tuple[0]))
            container_list.append({"container": tuple[0], "status": "NOK"})
            graph1["nodes"].append({"id": str(index), "label": tuple[0] + ":" + str(tuple[1]), "container": tuple[0], "port": tuple[1], "x": 0, "y": index, "size": 1, "color": "#000000"})
            # err = 1

    for index, tuple in enumerate(servers):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        app.logger.debug("Checking service:" + str(tuple))
        try:
            s.connect(tuple)
            s.close()
            app.logger.debug("\tConnected to " + str(tuple[0]))
            graph1["nodes"].append({"id": str(index + proxies_amount), "label": tuple[0] + ":" + str(tuple[1]), "container": tuple[0], "port": tuple[1], "x": 1, "y": index, "size": 1, "color": "#008cc2"})
        except socket.error as ex:
            app.logger.debug("\tConnection failed with errno {0}: {1}\n\tWaiting for".format(ex.errno, ex.strerror) + str(tuple[0]))
            container_list.append({"container": tuple[0], "status": "NOK"})
            graph1["nodes"].append({"id": str(index + proxies_amount), "label": tuple[0] + ":" + str(tuple[1]), "container": tuple[0], "port": tuple[1], "x": 1, "y": index, "size": 1, "color": "#000000"})

    for index, tuple in enumerate(databases):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        app.logger.debug("Checking service:" + str(tuple))
        try:
            s.connect(tuple)
            s.close()
            app.logger.debug("\tConnected to " + str(tuple[0]))
            graph1["nodes"].append({"id": str(index + proxies_amount + servers_amount), "label": tuple[0] + ":" + str(tuple[1]), "container": tuple[0], "port": tuple[1], "x": 2, "y": index, "size": 1, "color": "#008cc2"})
        except socket.error as ex:
            app.logger.debug("\tConnection failed with errno {0}: {1}\n\tWaiting for".format(ex.errno, ex.strerror) + str(tuple[0]))
            container_list.append({"container": tuple[0], "status": "NOK"})
            graph1["nodes"].append({"id": str(index + proxies_amount + servers_amount), "label": tuple[0] + ":" + str(tuple[1]), "container": tuple[0], "port": tuple[1], "x": 2, "y": index, "size": 1, "color": "#000000"})

    # for tuple in host_port_tuple_list:
    #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     app.logger.debug("Checking service:" + str(tuple))
    #     try:
    #         s.connect(tuple)
    #         s.close()
    #         app.logger.debug("\tConnected to " + str(tuple[0]))
    #         # container_list[tuple[0]] = {}"OK"
    #         container_list.append({"container": tuple[0], "status": "OK"})
    #     except socket.error as ex:
    #         app.logger.debug("\tConnection failed with errno {0}: {1}\n\tWaiting for".format(ex.errno, ex.strerror) + str(tuple[0]))
    #         # container_dict[tuple[1]] = "NOK"
    #         container_list.append({"container": tuple[0], "status": "NOK"})
    #         # err = 1

    return jsonify({"message": "OK", "healthcheck": graph1}), 200, {"Access-Control-Allow-Origin": "http://localhost:3535"}

######### HTML #########
@app.route('/', methods=['GET'])
def show_index():
    # return render_template('./home.html')
    return "<h1 style='color:red'>Hello<h1 style='color:yellow'> flask and world</h1>"
