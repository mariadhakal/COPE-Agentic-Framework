from abc import ABC, abstractmethod

class JavaParserInterface(ABC):
    @abstractmethod
    def java_code_parser(self, code: str) -> str:
        pass

class JavaProfilerInterface(ABC):
    @abstractmethod
    def profile_java_code(self, code: str, class_name: str, duration: int = 5) -> str:
        pass
