import os
import re
from zipfile import ZipFile

from werkzeug.utils import secure_filename

from .compile import CompilationHandler

UPLOAD_PATH_GOLANG=os.environ["UPLOAD_PATH_GOLANG"]
GO_INSTALLATION_PATH=os.environ["GO_INSTALLATION_PATH"]

class GolangCompilationHandler(CompilationHandler):
    """GolangCompilationHandler implements the abstract methods for Golang."""
    def __init__(self):
        super(GolangCompilationHandler, self).__init__(language="Golang", root_upload_path=UPLOAD_PATH_GOLANG)

    def compilation_options_parser(self, output_filename="", **kwargs):
        parsed_compilation_options = []

        secured_output_filename = secure_filename(output_filename)
        secured_output_filename = re.compile('^-+').sub('', secured_output_filename)
        if secured_output_filename == "":
            secured_output_filename = "a.out"

        return parsed_compilation_options, secured_output_filename

    def compilation_command_generator(self, working_directory, parsed_compilation_options, input_filename, output_filename):
        compile_command = ["go", "build"]
        compile_command.extend(parsed_compilation_options)
        compile_command.extend(["-o", working_directory + "/" + output_filename + ".wasm", working_directory + "/" + input_filename])
        return compile_command

    def results_zip_appender(self, working_directory, results_zip_name, output_filename, compression, compresslevel):
        with open(GO_INSTALLATION_PATH + "misc/wasm/wasm_exec.html", "r") as html_file_src:
            with open(working_directory + "/" + output_filename + ".html", "w") as html_file_dst:
                for line_num, line in enumerate(html_file_src, 1):
                    if line_num == 20:
                        html_file_dst.write(line.replace('wasm_exec.js', output_filename + ".js"))
                    elif line_num == 31:
                        html_file_dst.write(line.replace('test.wasm', output_filename + ".wasm"))
                    else:
                        html_file_dst.write(line)

        with ZipFile(file=working_directory + "/" + results_zip_name, mode="a", compression=compression, compresslevel=compresslevel) as results_zip:
            results_zip.write(working_directory + "/" + output_filename + ".html", output_filename + ".html")
            results_zip.write(GO_INSTALLATION_PATH + "misc/wasm/wasm_exec.js", output_filename + ".js")
            results_zip.write(working_directory + "/" + output_filename + ".wasm", output_filename + ".wasm")
