import json
import logging
import os
import re
import subprocess
from flask import Flask, jsonify, request, send_from_directory, make_response
from werkzeug.utils import secure_filename
from zipfile import ZipFile, ZIP_DEFLATED
#from flask_cors import CORS

# class c_compilation_options(object):
#     """docstring for ."""
#     def __init__(self, arg):
#         super().__init__()
#         self.optimization_level = optimization_level


UPLOAD_PATH_EMSCRIPTEN=os.environ.get("UPLOAD_PATH_EMSCRIPTEN", "/results/emscripten/")
COMPRESSION=ZIP_DEFLATED
COMPRESSLEVEL=6
app = Flask(__name__)
#CORS(app)

start_hyphen_sequence_pattern = re.compile('^-+')

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

# kwargs is used to throw away any unwanted arguments that come from the request
def parse_c_compilation_options(optimization_level="", iso_standard="", suppress_warnings=False, output_filename="", **kwargs):
    compile_command = ["emcc"]

    if optimization_level in ["O0", "O1", "O2", "O3", "Os", "Oz",]:
        compile_command.append("-" + optimization_level)

    if iso_standard in ["c89", "c90", "c99", "c11", "c17", "gnu89", "gnu90", "gnu99", "gnu11", "gnu17",]:
        compile_command.append("-std=" + iso_standard)

    if suppress_warnings == True:
        compile_command.append("-w")

    secured_output_filename = secure_filename(output_filename)
    if secured_output_filename == "":
        secured_output_filename = "a.out"
    else:
        secured_output_filename = start_hyphen_sequence_pattern.sub('', secured_output_filename)

    app.logger.debug("Parsed compile command: " + str(compile_command))
    app.logger.debug("Parsed Output Filename: " + secured_output_filename)

    return compile_command, secured_output_filename

def parse_cpp_compilation_options(optimization_level="", iso_standard="", suppress_warnings=False, output_filename="", **kwargs):
    compile_command = ["em++"]

    if optimization_level in ["O0", "O1", "O2", "O3", "Os", "Oz",]:
        compile_command.append("-" + optimization_level)

    if iso_standard in ["c++98", "c++03", "c++11", "c++14", "c++17", "c++2a",
        "gnu++98", "gnu++03", "gnu++11", "gnu++14", "gnu+++17", "gnu+++2a",]:
        compile_command.append("-std=" + iso_standard)

    if suppress_warnings == True:
        compile_command.append("-w")

    secured_output_filename = secure_filename(output_filename)
    if secured_output_filename == "":
        secured_output_filename = "a.out"
    else:
        secured_output_filename = start_hyphen_sequence_pattern.sub('', secured_output_filename)

    app.logger.debug("Parsed compile command: " + str(compile_command))
    app.logger.debug("Parsed Output Filename: " + secured_output_filename)

    return compile_command, secured_output_filename

############ API ############
@app.route('/compile', methods=['POST'])
def compile_c_or_cpp():
    if request.form["language"] == "C":
        return compile(UPLOAD_PATH_EMSCRIPTEN, parse_c_compilation_options)
    elif request.form["language"] == "C++":
        return compile(UPLOAD_PATH_EMSCRIPTEN, parse_cpp_compilation_options)

def compile(upload_path, parser):
    app.logger.debug(debug_request(request))

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

    subprocess.run(["ls", "-la", upload_path])

    try:
        client_file.save(upload_path + filename)
    except Exception:
        app.logger.exception("An error occured while saving: {filename}". format(filename=filename))
        return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500

    # TODO: check for mime type or make sure that it has ascii characters before compiling
    compile_command.extend(["-o", upload_path + secured_output_filename + ".html", upload_path + filename])
    app.logger.debug("Final compile command: " + str(compile_command))

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

    with ZipFile(file=upload_path + "results.zip", mode="w", compression=COMPRESSION, compresslevel=COMPRESSLEVEL) as results_zip:
        if completed_compile_file_process.stdout:
            results_zip.write(upload_path + "stdout.txt", "stdout.txt")

        if completed_compile_file_process.stderr:
            results_zip.write(upload_path + "stderr.txt", "stderr.txt")

    # TODO: Activate X-Sendfile
    if completed_compile_file_process.returncode == 0:
        return_status_code = 200
        with ZipFile(file=upload_path + "results.zip", mode="a", compression=COMPRESSION, compresslevel=COMPRESSLEVEL) as results_zip:
            results_zip.write(upload_path + secured_output_filename + ".html", secured_output_filename + ".html")
            results_zip.write(upload_path + secured_output_filename + ".js", secured_output_filename + ".js")
            results_zip.write(upload_path + secured_output_filename + ".wasm", secured_output_filename + ".wasm")
    else:
        return_status_code = 400

    response = make_response(send_from_directory(upload_path, "results.zip", as_attachment=True), return_status_code)
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3535"
    response.headers["Content-Type"] = "application/zip"
    app.logger.debug(response.headers)
    app.logger.debug(response.__dict__)
    app.logger.debug(response.response.__dict__)
    subprocess.run(["ls", "-la", upload_path])
    return response

######### HTML #########
@app.route('/', methods=['GET'])
def show_index():
    # return render_template('./home.html')
    return "<h1 style='color:red'>Hello<h1 style='color:yellow'> flask and world</h1>"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
