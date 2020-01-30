from flask import Flask, jsonify, request, send_from_directory, make_response
import logging
import subprocess
import os
from werkzeug.utils import secure_filename
from zipfile import ZipFile
#from flask_cors import CORS

UPLOAD_PATH_EMSCRIPTEN=os.environ.get("UPLOAD_PATH_EMSCRIPTEN", "/results/emscripten/")
app = Flask(__name__)
#CORS(app)

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

############ API ############
@app.route('/compile', methods=['POST'])
def compile():
    app.logger.debug(debug_request(request))

    client_file = request.files["mycode"]
    filename = secure_filename(client_file.filename)

    app.logger.debug("File information: " + str(client_file))
    app.logger.debug("Secure Filename: " + filename)
    app.logger.debug("Content-type: " + client_file.content_type)

    # file_content = request.files["mycode"].read()
    # app.logger.debug(file_content)
    subprocess.run(["ls", "-la", UPLOAD_PATH_EMSCRIPTEN])

    try:
        client_file.save(UPLOAD_PATH_EMSCRIPTEN + filename)
    except Exception:
        app.logger.exception("An error occured while saving: {filename}". format(filename=filename))
        return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500

    # app.logger.debug("\n" + file_content.decode("ascii"))
    # TODO: check for mime type or make sure that it has ascii characters before compiling
    compile_command = ["emcc", UPLOAD_PATH_EMSCRIPTEN + filename, "-o", UPLOAD_PATH_EMSCRIPTEN + filename + ".html"]
    try:
        # DONT USE shell=True for security and vulnerabilities
        completed_compile_file_process = subprocess.run(compile_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if completed_compile_file_process.stdout:
            with open(UPLOAD_PATH_EMSCRIPTEN + "stdout.txt", "w") as f:
                print(completed_compile_file_process.stdout.decode(encoding="utf-8"), file=f)

        if completed_compile_file_process.stderr:
            with open(UPLOAD_PATH_EMSCRIPTEN + "stderr.txt", "w") as f:
                print(completed_compile_file_process.stderr.decode(encoding="utf-8"), file=f)

    except Exception:
        subprocess.run(["ls", "-la", UPLOAD_PATH_EMSCRIPTEN])
        app.logger.exception("An error occured during: subprocess.run({compile_command})".format(compile_command=compile_command))
        return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500

    subprocess.run(["ls", "-la", UPLOAD_PATH_EMSCRIPTEN])
    app.logger.debug("Compilation return code: " + str(completed_compile_file_process.returncode))

    # TODO: Activate X-Sendfile
    if completed_compile_file_process.returncode == 0:
        with ZipFile(UPLOAD_PATH_EMSCRIPTEN + "results.zip", "w") as results_zip:
            results_zip.write(UPLOAD_PATH_EMSCRIPTEN + filename + ".html", filename + ".html")
            results_zip.write(UPLOAD_PATH_EMSCRIPTEN + filename + ".js", filename + ".js")
            results_zip.write(UPLOAD_PATH_EMSCRIPTEN + filename + ".wasm", filename + ".wasm")

        response = make_response(send_from_directory(UPLOAD_PATH_EMSCRIPTEN, "results.zip"), 201)
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3535"
        return response
    return jsonify({'message': 'OK', 'file_content': 42}), 201, {'Access-Control-Allow-Origin': 'http://localhost:3535'}

######### HTML #########
@app.route('/', methods=['GET'])
def show_index():
    # return render_template('./home.html')
    return "<h1 style='color:red'>Hello<h1 style='color:yellow'> flask and world</h1>"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
