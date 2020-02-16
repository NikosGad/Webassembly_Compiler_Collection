from werkzeug.utils import secure_filename
# kwargs is used to throw away any unwanted arguments that come from the request
def parse_c_compilation_options(optimization_level="", iso_standard="", suppress_warnings=False, output_filename="", **kwargs):
    compile_command = ["emcc"]

    print(optimization_level)
    print(type(optimization_level))
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
        secured_output_filename = start_hyphen_sequence_pattern.sub('', secured_output_filename)

    return compile_command, secured_output_filename
