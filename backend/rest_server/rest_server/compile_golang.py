import re
from werkzeug.utils import secure_filename
from zipfile import ZipFile

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
    # with ZipFile(file=working_directory + results_zip_name, mode=mode, compression=compression, compresslevel=compresslevel) as results_zip:
    #     results_zip.write(working_directory + output_filename + ".html", output_filename + ".html")
    #     results_zip.write(working_directory + output_filename + ".js", output_filename + ".js")
    #     results_zip.write(working_directory + output_filename + ".wasm", output_filename + ".wasm")
    #     results_zip.write(UPLOAD_PATH_GOLANG + "index.html", "index.html")
    #     results_zip.write(UPLOAD_PATH_GOLANG + "wasm_exec.js", "wasm_exec.js")
    #     results_zip.write(UPLOAD_PATH_GOLANG + secured_output_filename + ".wasm", secured_output_filename + ".wasm")
    pass
