from fastapi import APIRouter, Depends, HTTPException
from services.base import JavaParserInterface, JavaProfilerInterface
from dependencies import get_parser_service, get_profiler_service
import json

router = APIRouter()

@router.post("/parse")
def parse_code(code: str, parser: JavaParserInterface = Depends(get_parser_service)):
    return {"parsed": parser.parse(code)}

@router.post("/profile")
def profile_code(code: str, class_name: str, duration: int = 5,
                 profiler: JavaProfilerInterface = Depends(get_profiler_service)):
    return json.loads(profiler.profile(code, class_name, duration))
