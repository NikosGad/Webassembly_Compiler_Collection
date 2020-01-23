from flask import Flask, jsonify, request
import logging
#from flask_cors import CORS

app = Flask(__name__)
#CORS(app)

############ API ############
@app.route('/compile', methods=['POST'])
def compile():
    client_request = request.json
    app.logger.debug("REQUEST: " + str(request))
    app.logger.debug("REQUEST FILES DICTIONARY: " + str(request.files))
    app.logger.debug("REQUEST TEXT FIELDS DICTIONARY: " + str(request.form))
    app.logger.debug("REQUEST RAW JSON: " + str(client_request))
    app.logger.debug("Handling POST request: Start compilation of " + str(request.files["mycode"]))
    file_content = request.files["mycode"].read()
    app.logger.debug(file_content.decode("ascii"))
    return jsonify({'message': 'OK', 'file_content': file_content.decode("ascii")}), 201

######### HTML #########
@app.route('/', methods=['GET'])
def show_index():
    # return render_template('./home.html')
    return "<h1 style='color:red'>Hello<h1 style='color:yellow'> flask and world</h1>"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
