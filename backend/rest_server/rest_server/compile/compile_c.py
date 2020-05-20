import os
import re
from zipfile import ZipFile

from werkzeug.utils import secure_filename

from .compile import CompilationHandler

UPLOAD_PATH_EMSCRIPTEN=os.environ["UPLOAD_PATH_EMSCRIPTEN"]

class CCompilationHandler(CompilationHandler):
    """CCompilationHandler implements the abstract methods for C."""
    def __init__(self):
        super(CCompilationHandler, self).__init__(language="C", root_upload_path=UPLOAD_PATH_EMSCRIPTEN)

    # kwargs is used to throw away any unwanted arguments that come from the request
    def compilation_options_parser(self, optimization_level="", iso_standard="", suppress_warnings=False, output_filename="", **kwargs):
        parsed_compilation_options = []

        if optimization_level in ["O0", "O1", "O2", "O3", "Os", "Oz",]:
            parsed_compilation_options.append("-" + optimization_level)

        if iso_standard in ["c89", "c90", "c99", "c11", "c17", "gnu89", "gnu90", "gnu99", "gnu11", "gnu17",]:
            parsed_compilation_options.append("-std=" + iso_standard)

        if suppress_warnings == True:
            parsed_compilation_options.append("-w")

        secured_output_filename = secure_filename(output_filename)
        secured_output_filename = re.compile('^-+').sub('', secured_output_filename)
        if secured_output_filename == "":
            secured_output_filename = "a.out"

        return parsed_compilation_options, secured_output_filename

    def compilation_command_generator(self, working_directory, parsed_compilation_options, input_filename, output_filename):
        compilation_command = ["emcc"]
        compilation_command.extend(parsed_compilation_options)
        compilation_command.extend(["-o", working_directory + output_filename + ".html", working_directory + input_filename])
        return compilation_command

    def results_zip_appender(self, working_directory, results_zip_name, output_filename, mode, compression, compresslevel):
        with ZipFile(file=working_directory + results_zip_name, mode=mode, compression=compression, compresslevel=compresslevel) as results_zip:
            results_zip.write(working_directory + output_filename + ".html", output_filename + ".html")
            results_zip.write(working_directory + output_filename + ".js", output_filename + ".js")
            results_zip.write(working_directory + output_filename + ".wasm", output_filename + ".wasm")
