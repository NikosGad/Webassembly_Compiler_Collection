import os
import subprocess

from flask import g, jsonify, make_response, request, send_from_directory
from werkzeug.utils import secure_filename

from rest_server import app
from .. import authentication
from ..models import file_model
from ..compile import compilation_handlers_dictionary

@app.route('/api/files/personal_file_content', methods=['GET'])
@authentication.Authentication.authentication_required
def get_personal_file_content():
    language = request.args.get("language")
    directory = request.args.get("directory")
    name = request.args.get("name")
    if not language or not directory or not name:
        return jsonify({"type": "GetFileError", "message": "A language, a directory and a name query parameters should be provided."}), 400

    secured_directory = secure_filename(directory)
    secured_name = secure_filename(name)
    compilation_handler = compilation_handlers_dictionary.get(language)
    if not compilation_handler:
        return jsonify({"type": "GetFileError", "message": "Language {} is not supported.".format(language)}), 400

    path = compilation_handler.root_upload_path + str(g.user["id"]) + "/" + secured_directory + "/"

    if not os.path.isfile(path + secured_name):
        app.logger.debug("File: {} does not exist".format(path + secured_name))
        return jsonify({"type": "FileNotFound", "message": "The file could not be found. Are you sure it should exists? If this was an existing file that belonged to you, please try to delete it and re-upload it."}), 404

    app.logger.debug("File exists in path: " + path + secured_name)
    response = make_response(send_from_directory(path, secured_name, as_attachment=True), 200)
    return response

@app.route('/api/files/all_personal', methods=['GET'])
@authentication.Authentication.authentication_required
def get_personal_files():
    try:
        files = file_model.SourceCodeFile.get_files_per_language_by_user_id(g.user["id"])
        app.logger.debug(files)
        return jsonify(dict(files)), 200
    except Exception as e:
        app.logger.exception("Error Getting Personal Files for UserID: {}".format(g.user.get("id")))
        return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500

@app.route('/api/files/personal_file/<file_id>', methods=['DELETE'])
@authentication.Authentication.authentication_required
def delete_personal_file_directory(file_id):
    try:
        file_id_int = int(file_id)
        if file_id_int <= 0:
            return jsonify({"type": "FileIDTypeError", "message": "File ID value should be a positive integer"}), 400
    except ValueError as e:
        return jsonify({"type": "FileIDTypeError", "message": "File ID value should be a positive integer"}), 400

    try:
        file = file_model.SourceCodeFile.get_file_by_file_id_and_user_id(file_id_int, g.user["id"])
        app.logger.debug("Retrieved File: " + str(file))
    except Exception as e:
        app.logger.exception("Unexpected Error Getting File with ID: {} for User ID: {} from DB in Delete File".format(file_id_int, g.user.get("id")))
        return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500

    if not file:
        return jsonify({"type": "FileNotFound", "message": "The file you are trying to delete does not exist"}), 404

    directory_path = compilation_handlers_dictionary[file.language].root_upload_path + str(g.user["id"]) + "/" + file.directory

    if not os.path.isdir(directory_path):
        app.logger.error("Inconsistency during delete of file: {}\nPath {} does not exist".format(file, directory_path))
    else:
        app.logger.debug("Deleting path: " + directory_path)
        completed_delete_process = subprocess.run(["rm", "-r", directory_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if completed_delete_process.stdout:
            app.logger.info(completed_delete_process.stdout.decode(encoding="utf-8"))

        if completed_delete_process.returncode != 0:
            app.logger.error("Failed to delete directory")
            if completed_delete_process.stderr:
                app.logger.error(completed_delete_process.stderr.decode(encoding="utf-8"))

            return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500
        else:
            app.logger.info("Deleted directory: " + directory_path)

    try:
        file.delete()
        app.logger.info("Deleted file from DB: " + str(file))
        return jsonify({"message": "OK"}), 200
    except Exception as e:
        app.logger.exception("Unexpected Error Deleting File with ID: {} from DB in Delete File".format(file_id_int))
        return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500
