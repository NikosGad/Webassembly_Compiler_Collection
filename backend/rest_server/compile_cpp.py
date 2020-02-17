import re
from werkzeug.utils import secure_filename

def parse_cpp_compilation_options(optimization_level="", iso_standard="", suppress_warnings=False, output_filename="", **kwargs):
    compile_command = ["em++"]

    if optimization_level in ["O0", "O1", "O2", "O3", "Os", "Oz",]:
        compile_command.append("-" + optimization_level)

    if iso_standard in ["c++98", "c++03", "c++11", "c++14", "c++17", "c++2a",
        "gnu++98", "gnu++03", "gnu++11", "gnu++14", "gnu+++17", "gnu+++2a",]:
        compile_command.append("-std=" + iso_standard)

    if suppress_warnings == True:
        compile_command.append("-w")

    secured_output_filename = secure_filename(output_filename)
    if secured_output_filename == "":
        secured_output_filename = "a.out"
    else:
        secured_output_filename = re.compile('^-+').sub('', secured_output_filename)

    return compile_command, secured_output_filename

def generate_cpp_compile_command(working_directory, parsed_compilation_options, input_filename, output_filename):
    parsed_compilation_options.extend(["-o", working_directory + output_filename + ".html", working_directory + input_filename])
    return parsed_compilation_options
