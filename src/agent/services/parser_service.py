from services.base import JavaParserInterface
from utils.java_code_parser import java_parser

class JavaParserService(JavaParserInterface):
    def parser(self, code: str) -> str:
        return java_parser(code)
