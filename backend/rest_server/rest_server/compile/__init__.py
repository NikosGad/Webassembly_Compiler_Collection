from .compile_c import CCompilationHandler
from .compile_cpp import CppCompilationHandler
from .compile_golang import GolangCompilationHandler

compilation_handlers_dictionary = {
    "C": CCompilationHandler(),
    "Cpp": CppCompilationHandler(),
    "Golang": GolangCompilationHandler()
}
