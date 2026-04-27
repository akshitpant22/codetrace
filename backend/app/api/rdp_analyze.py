from fastapi import APIRouter
from pydantic import BaseModel

from app.core.rdp_parser import compare_trees, get_parse_tree

router = APIRouter(prefix="/api", tags=["rdp_analyze"])

class RDPAnalyzeRequest(BaseModel):
    code1: str
    code2: str

@router.post("/rdp-analyze")
def analyze_rdp(request: RDPAnalyzeRequest):
    tree1 = get_parse_tree(request.code1)
    tree2 = get_parse_tree(request.code2)
    raw_score = compare_trees(request.code1, request.code2)
    percentage_score = round(raw_score * 100, 2)
    if percentage_score <= 30.0:
        verdict = "Not Plagiarized"
    elif percentage_score <= 70.0:
        verdict = "Possibly Plagiarized"
    else:
        verdict = "Plagiarized"
    return {
        "parse_tree1": tree1,
        "parse_tree2": tree2,
        "similarity_score": percentage_score,
        "verdict": verdict
    }
