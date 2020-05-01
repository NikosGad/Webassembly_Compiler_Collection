import os

from .compile_c import CCompilationHandler
from .compile_cpp import CppCompilationHandler
from .compile_golang import GolangCompilationHandler

UPLOAD_PATH_EMSCRIPTEN=os.environ["UPLOAD_PATH_EMSCRIPTEN"]
UPLOAD_PATH_GOLANG=os.environ["UPLOAD_PATH_GOLANG"]

compilation_handlers_dictionary = {
    "C": CCompilationHandler("C", UPLOAD_PATH_EMSCRIPTEN),
    "Cpp": CppCompilationHandler("Cpp", UPLOAD_PATH_EMSCRIPTEN),
    "Golang": GolangCompilationHandler("Golang", UPLOAD_PATH_GOLANG)
}
