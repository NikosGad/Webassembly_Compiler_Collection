import abc
import copy
import datetime
import hashlib
import json
import os
import shutil
import subprocess

from flask import g, jsonify, make_response, request, send_from_directory
from werkzeug.utils import secure_filename
from zipfile import ZipFile, ZIP_DEFLATED

from rest_server import app
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

    def __repr__(self): # pragma: no cover
        return "<Object of {} at {}: CompilationHandler({!r}, {!r})>".format(self.__class__, hex(id(self)), self.language, self.root_upload_path)

    @abc.abstractmethod
    def compilation_options_parser(self, *args, **kwargs):
        pass # pragma: no cover

    @abc.abstractmethod
    def compilation_command_generator(self, *args, **kwargs):
        pass # pragma: no cover

    @abc.abstractmethod
    def results_zip_appender(self, *args, **kwargs):
        pass # pragma: no cover

    def _generate_file_subpath(self, client_file):
        sha256_hash = hashlib.sha256()

        for byte_block in iter(lambda: client_file.read(4096),b""):
            sha256_hash.update(byte_block)

        # Rewind file pointer to the beginning
        client_file.seek(0)

        return str(datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S%f")) + "_" + sha256_hash.hexdigest()

    def _format_full_file_path(self, user_id, unique_file_subpath):
        return self.root_upload_path + "/" + user_id + "/" + unique_file_subpath[-3:] + "/" + unique_file_subpath

    def compile(self, client_file, compilation_options_json, store=False):
        try:
            filename = secure_filename(client_file.filename)
            app.logger.debug("Secure Filename: " + filename)

            subpath = self._generate_file_subpath(client_file)
            if store:
                user_id = str(g.user["id"])
            else:
                user_id = "unknown"

            upload_path = self._format_full_file_path(user_id, subpath)

            try:
                compilation_options_dict = json.loads(compilation_options_json)
            except Exception:
                app.logger.info("An error occured while loading incorrect compilation options json")
                return jsonify({"type": "JSONParseError", "message": "Bad JSON Format Error"}), 400

            parsed_compilation_options, secured_output_filename = self.compilation_options_parser(**compilation_options_dict)
            app.logger.debug("Parsed compilation options: " + str(parsed_compilation_options))
            app.logger.debug("Parsed Output Filename: " + secured_output_filename)

            compile_command = self.compilation_command_generator(upload_path, parsed_compilation_options, filename, secured_output_filename)
            app.logger.debug("Compile command: " + str(compile_command))

            try:
                os.makedirs(upload_path)
                app.logger.info("Path generated: " + upload_path)
            except FileExistsError:
                app.logger.error("Path exists: " + upload_path)
                return jsonify({"type": "FileExistsError", "message": "The uploaded file already exists"}), 400

            client_file.save(upload_path + "/" + filename)

            # DONT USE shell=True for security and vulnerabilities
            completed_compile_file_process = subprocess.run(compile_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if completed_compile_file_process.stdout:
                with open(upload_path + "/stdout.txt", "w") as f_out:
                    print(completed_compile_file_process.stdout.decode(encoding="utf-8"), file=f_out)

            if completed_compile_file_process.stderr:
                with open(upload_path + "/stderr.txt", "w") as f_err:
                    print(completed_compile_file_process.stderr.decode(encoding="utf-8"), file=f_err)

            app.logger.info("Compilation return code in path {path}: {return_code}".format(path=upload_path, return_code=str(completed_compile_file_process.returncode)))

            with ZipFile(file=upload_path + "/" + RESULTS_ZIP_NAME, mode="w", compression=COMPRESSION, compresslevel=COMPRESSLEVEL) as results_zip:
                if completed_compile_file_process.stdout:
                    results_zip.write(upload_path + "/stdout.txt", "stdout.txt")

                if completed_compile_file_process.stderr:
                    results_zip.write(upload_path + "/stderr.txt", "stderr.txt")

            # TODO: Activate X-Sendfile
            if completed_compile_file_process.returncode == 0:
                return_status_code = 200
                compilation_status = "Successful"
                self.results_zip_appender(upload_path, RESULTS_ZIP_NAME, secured_output_filename, COMPRESSION, COMPRESSLEVEL)
            else:
                return_status_code = 400
                compilation_status = "Erroneous"

            if store:
                file_dictionary = {
                    "user_id": g.user["id"],
                    "name": filename,
                    "directory": subpath,
                    "compilation_options": parsed_compilation_options,
                    "language": self.language,
                    "status": compilation_status,
                }
                file_db = file_model.SourceCodeFile(**file_dictionary)
                file_db.create()
                app.logger.info("File in path {path} is saved in DB".format(path=upload_path))

            response = make_response(send_from_directory(upload_path, RESULTS_ZIP_NAME, as_attachment=True), return_status_code)
            response.headers["Content-Type"] = "application/zip"
            app.logger.debug(response.headers)
            app.logger.debug(response.__dict__)
            app.logger.debug(response.response.__dict__)
            return response
        except Exception:
            app.logger.exception("Unexpected error occured during compile()")
            app.logger.warning("Asserting that no orphaned directory is created...")
            try:
                upload_path
            except UnboundLocalError as e:
                upload_path = ""

            if os.path.isdir(upload_path):
                app.logger.warning("Detected orphaned directory: " + upload_path)
                shutil.rmtree(upload_path)
                app.logger.info("Orphaned directory deleted: " + upload_path)
            else:
                app.logger.info("No orphaned directory is created")

            return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500
