import abc
import copy
import json
import os
import subprocess

from flask import g, jsonify, make_response, request, send_from_directory
from werkzeug.utils import secure_filename
from zipfile import ZipFile, ZIP_DEFLATED

from rest_server import app
from .. import common
from ..models import file_model

RESULTS_ZIP_NAME="results.zip"
COMPRESSION=ZIP_DEFLATED
COMPRESSLEVEL=6

class CompilationHandler(metaclass=abc.ABCMeta):
    """CompilationHandler is an abstract class that declares all the necessary \
methods that a language specific compilation handler should implement."""
    def __init__(self, language, root_upload_path):
        self.language = language
        self.root_upload_path = root_upload_path

    def __repr__(self):
        return "<Object of {} at {}: CompilationHandler({!r}, {!r})>".format(self.__class__, hex(id(self)), self.language, self.root_upload_path)

    @abc.abstractmethod
    def compilation_options_parser(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def compilation_command_generator(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def results_zip_appender(self, *args, **kwargs):
        pass

    def compile(self, client_file, compilation_options_json, store=False):
        filename = secure_filename(client_file.filename)
        app.logger.debug("Secure Filename: " + filename)

        subpath = common.generate_file_subpath(client_file)
        if store:
            user_id = str(g.user["id"])

            file_dictionary = {
                "user_id": g.user["id"],
                "name": filename,
                "directory":subpath,
                "language": self.language,
            }
        else:
            user_id = "unknown"

        upload_path = self.root_upload_path + user_id + "/" + subpath + "/"

        try:
            compilation_options_dict = json.loads(compilation_options_json)
        except Exception:
            app.logger.debug("An error occured while loading compilation options json")
            return jsonify({"type": "JSONParseError", "message": "Bad JSON Format Error"}), 400

        parsed_compile_options, secured_output_filename = self.compilation_options_parser(**compilation_options_dict)
        app.logger.debug("Parsed compile options: " + str(parsed_compile_options))
        app.logger.debug("Parsed Output Filename: " + secured_output_filename)

        if store:
            file_dictionary["compilation_options"] = copy.copy(parsed_compile_options)

        compile_command = self.compilation_command_generator(upload_path, parsed_compile_options, filename, secured_output_filename)
        app.logger.debug("Final compile command: " + str(compile_command))

        try:
            os.makedirs(upload_path)
            app.logger.debug("Path generated: " + upload_path)
        except FileExistsError:
            app.logger.exception("Path exists: " + upload_path)
            return jsonify({"type": "FileExistsError", "message": "The uploaded file already exists"}), 400

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
            if store:
                file_dictionary["status"] = "Successful"
            self.results_zip_appender(upload_path, RESULTS_ZIP_NAME, secured_output_filename, "a", COMPRESSION, COMPRESSLEVEL)
        else:
            if store:
                file_dictionary["status"] = "Erroneous"
            return_status_code = 400

        try:
            if store:
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
