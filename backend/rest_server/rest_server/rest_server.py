from rest_server import app
from rest_server import db
from rest_server import UPLOAD_PATH_EMSCRIPTEN, UPLOAD_PATH_GOLANG, ROOT_UPLOAD_PATHS
from flask import g, jsonify, request, send_from_directory, make_response

from . import authentication
from .models import user_model
from .models import file_model

from . import common
from .compile.compile import compile, compile_and_store_in_DB
from .compile import compile_c
from .compile import compile_cpp
from .compile import compile_golang

user_schema = user_model.UserSchema()
file_schema = file_model.SourceCodeFileSchema()

############ API ############

######### HTML #########
@app.route('/', methods=['GET'])
def show_index():
    # return render_template('./home.html')
    return "<h1 style='color:red'>Hello<h1 style='color:yellow'> flask and world</h1>"
