import re
from werkzeug.utils import secure_filename

# kwargs is used to throw away any unwanted arguments that come from the request
def parse_c_compilation_options(optimization_level="", iso_standard="", suppress_warnings=False, output_filename="", **kwargs):
    compile_command = ["emcc"]

    if optimization_level in ["O0", "O1", "O2", "O3", "Os", "Oz",]:
        compile_command.append("-" + optimization_level)

    if iso_standard in ["c89", "c90", "c99", "c11", "c17", "gnu89", "gnu90", "gnu99", "gnu11", "gnu17",]:
        compile_command.append("-std=" + iso_standard)

    if suppress_warnings == True:
        compile_command.append("-w")

    secured_output_filename = secure_filename(output_filename)
    if secured_output_filename == "":
        secured_output_filename = "a.out"
    else:
        secured_output_filename = re.compile('^-+').sub('', secured_output_filename)

    return compile_command, secured_output_filename

# In order to allow other function for different languages to have different
# handling, this function shall return the parsed_compilation_options parameter.
# With this implementation, this is unnecessary because the initial argument
# that was passed in this function will also be altered and in the end it will
# still be pointing to the same list. Thus we are returning a pointer to a list
# that the caller function already has.
# However, another function may return a list that is generated exclusively
# inside it, thus the caller function does not already have a pointer to this
# list, so the list needs to be returned from the callee function.
# In order to have a uniform design, this function shall return a list value.
def generate_c_compile_command(working_directory, parsed_compilation_options, input_filename, output_filename):
    # TODO: check for mime type or make sure that it has ascii characters before compiling
    parsed_compilation_options.extend(["-o", working_directory + output_filename + ".html", working_directory + input_filename])
    return parsed_compilation_options
