from pydantic import BaseModel
from typing import List, Optional

class CodeAnalysisRequest(BaseModel):
    language: str
    code: str

class AnalysisResult(BaseModel):
    line: int
    name: str
    rule_id: str
    message: str
    severity: str = "warning"  # warning, error, info

class CodeAnalysisResponse(BaseModel):
    results: List[AnalysisResult]
    total_issues: int
    parser_errors: List[dict] = []
