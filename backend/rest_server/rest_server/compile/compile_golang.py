import re
import os
from werkzeug.utils import secure_filename
from zipfile import ZipFile

GO_INSTALLATION_PATH=os.environ.get("GO_INSTALLATION_PATH", "usr/local/go/")

def parse_golang_compilation_options(output_filename="", **kwargs):
    compile_command = ["go", "build"]

    secured_output_filename = secure_filename(output_filename)
    if secured_output_filename == "":
        secured_output_filename = "a.out"
    else:
        secured_output_filename = re.compile('^-+').sub('', secured_output_filename)

    return compile_command, secured_output_filename

def generate_golang_compile_command(working_directory, parsed_compilation_options, input_filename, output_filename):
    parsed_compilation_options.extend(["-o", working_directory + output_filename + ".wasm", working_directory + input_filename])
    return parsed_compilation_options

def append_golang_results_zip(working_directory, results_zip_name, output_filename, mode, compression, compresslevel):
    line_num = 1
    with open(GO_INSTALLATION_PATH + "misc/wasm/wasm_exec.html", "r") as html_file_src:
        with open(working_directory + output_filename + ".html", "w") as html_file_dst:
            for line in html_file_src:
                if line_num == 20:
                    html_file_dst.write(line.replace('wasm_exec.js', output_filename + ".js"))
                elif line_num == 31:
                    html_file_dst.write(line.replace('test.wasm', output_filename + ".wasm"))
                else:
                    html_file_dst.write(line)

                line_num += 1;

    with ZipFile(file=working_directory + results_zip_name, mode=mode, compression=compression, compresslevel=compresslevel) as results_zip:
        results_zip.write(working_directory + output_filename + ".html", output_filename + ".html")
        results_zip.write(GO_INSTALLATION_PATH + "misc/wasm/wasm_exec.js", output_filename + ".js")
        results_zip.write(working_directory + output_filename + ".wasm", output_filename + ".wasm")
