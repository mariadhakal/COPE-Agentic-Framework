from services.base import JavaParserInterface, JavaProfilerInterface
from core.java_profiler import JavaProfiler
import json

class JavaProfilerService(JavaProfilerInterface):
    def profile(self, code: str, class_name: str, duration: int = 10) -> str:
        profiler = JavaProfiler()
        result = profiler.profile_code(code, class_name, duration)
        return json.dumps(result)

