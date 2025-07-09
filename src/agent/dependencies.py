from services.parser_service import JavaParserService
from services.profile_service import JavaProfilerService

def get_parser_service():
    return JavaParserService()

def get_profiler_service():
    return JavaProfilerService()
