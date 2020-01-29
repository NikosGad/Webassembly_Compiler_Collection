from flask import Flask, jsonify, request
import logging
import subprocess
from werkzeug.utils import secure_filename
#from flask_cors import CORS

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
    app.logger.debug("Start compilation of " + str(client_file))
    app.logger.debug(client_file.content_type)
    app.logger.debug(client_file.filename)
    filename = secure_filename(client_file.filename)
    app.logger.debug(filename)
    # file_content = request.files["mycode"].read()
    # app.logger.debug(file_content)
    subprocess.run(["ls", "-la", "/results"])
    client_file.save("/results/"+filename)

    # app.logger.debug("\n" + file_content.decode("ascii"))
    # TODO: check for mime type or make sure that it has ascii characters before compiling 
    # compile_command = ["ls", "-la"]
    compile_command = ["emcc", "/results/"+filename, "-o", "/results/"+filename+".html"]
    try:
        # DONT USE shell=True for security and vulnerabilities
        completed_compile_file_process = subprocess.run(compile_command)
        subprocess.run(["ls", "-la", "/results"])
    except Exception:
        app.logger.exception("An error occured during: subprocess.run({compile_command})".format(compile_command=compile_command))
        return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500

    app.logger.debug(completed_compile_file_process.returncode)
    return jsonify({'message': 'OK', 'file_content': 42}), 201, {'Access-Control-Allow-Origin': 'http://localhost:3535'}

######### HTML #########
@app.route('/', methods=['GET'])
def show_index():
    # return render_template('./home.html')
    return "<h1 style='color:red'>Hello<h1 style='color:yellow'> flask and world</h1>"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
