import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.detector import detect_plagiarism
from app.dependencies import get_current_user, get_db
from app.models.result import Result
from app.models.user import User
from app.schemas.result import ResultResponse

router = APIRouter(prefix="/api", tags=["analyze"])

ALLOWED_EXTENSIONS = {".py", ".c", ".cpp", ".java", ".js", ".ts"}

def _is_allowed_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename or "")
    return ext.lower() in ALLOWED_EXTENSIONS

@router.post("/analyze", response_model=ResultResponse)
def analyze_code(
    file1: Annotated[UploadFile, File(..., description="First code file")],
    file2: Annotated[UploadFile, File(..., description="Second code file")],
    language: Annotated[str, Form(...)],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _is_allowed_file(file1.filename) or not _is_allowed_file(file2.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Both files must have a supported extension: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    try:
        code1 = file1.file.read().decode("utf-8")
        code2 = file2.file.read().decode("utf-8")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error reading uploaded files. Ensure they are UTF-8 encoded text.",
        )

    if not code1.strip() or not code2.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both code files must be non-empty.",
        )

    try:
        result = detect_plagiarism(code1, code2, language)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detection failed: {str(e)}",
        )

    db_result = Result(
        file1_name=os.path.basename(file1.filename),
        file2_name=os.path.basename(file2.filename),
        language=language,
        lexical_score=result["lexical_score"],
        syntax_score=result["syntax_score"],
        semantic_score=result["semantic_score"],
        cfg_score=result["cfg_score"],
        pdg_score=result["pdg_score"],
        final_score=result["final_score"],
        verdict=result["verdict"],
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)

    return ResultResponse.model_validate(db_result)
