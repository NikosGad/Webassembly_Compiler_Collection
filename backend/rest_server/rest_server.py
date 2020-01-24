from flask import Flask, jsonify, request
import logging
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
    client_request = request.json
    app.logger.debug(debug_request(request))
    app.logger.debug("Start compilation of " + str(request.files["mycode"]))
    file_content = request.files["mycode"].read()
    app.logger.debug("\n" + file_content.decode("ascii"))
    return jsonify({'message': 'OK', 'file_content': file_content.decode("ascii")}), 201, {'Access-Control-Allow-Origin': 'http://localhost:3535'}

######### HTML #########
@app.route('/', methods=['GET'])
def show_index():
    # return render_template('./home.html')
    return "<h1 style='color:red'>Hello<h1 style='color:yellow'> flask and world</h1>"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
