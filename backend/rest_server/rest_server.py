from flask import Flask, jsonify, request
import logging
#from flask_cors import CORS

app = Flask(__name__)
#CORS(app)

############ API ############
@app.route('/compile', methods=['POST'])
def compile():
    client_request = request.json
    app.logger.debug("Handling POST request: Start compilation of " + str(client_request))
    return jsonify({'message': 'OK'}), 201

######### HTML #########
@app.route('/', methods=['GET'])
def show_index():
    # return render_template('./home.html')
    return "Hello index"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
