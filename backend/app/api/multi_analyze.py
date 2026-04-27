import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.multi_analyzer import analyze_multiple, get_suspicious_pairs
from app.dependencies import get_current_user, get_db
from app.models.multi_result import MultiSession, MultiPairResult
from app.models.user import User
from app.schemas.multi_result import MultiAnalysisResponse

router = APIRouter(prefix="/api", tags=["multi-analyze"])

ALLOWED_EXTENSIONS = {".py", ".c", ".cpp", ".java", ".js", ".ts"}

def _is_allowed_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename or "")
    return ext.lower() in ALLOWED_EXTENSIONS

@router.post("/multi-analyze", response_model=MultiAnalysisResponse)
async def analyze_multiple_files(
    files: List[UploadFile] = File(...),
    language: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analyzes multiple files, comparing every possible pair against each other.
    Validates limits (2-10 files), parses contents, computes similarity matrix,
    persists results to the database, and returns suspicious mappings.
    """
    if len(files) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must upload at least 2 files for multi-file analysis."
        )
        
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files allowed per analysis."
        )
    for f in files:
        if not _is_allowed_file(f.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {f.filename} has an unsupported extension. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
    files_data = []
    for f in files:
        try:
            raw_bytes = await f.read()
            content = raw_bytes.decode("utf-8")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error reading file {f.filename}. Ensure it is UTF-8 encoded text."
            )
            
        if not content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {f.filename} is empty."
            )
            
        files_data.append((os.path.basename(f.filename), content))
    try:
        matrix = analyze_multiple(files_data, language)
        suspicious_pairs = get_suspicious_pairs(matrix)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-file detection failed: {str(e)}",
        )
    db_session = MultiSession(
        total_files=len(files_data),
        language=language
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    for pair_key, data in matrix.items():
        result = data["result"]
        db_pair = MultiPairResult(
            session_id=db_session.session_id,
            file1_name=data["file1"],
            file2_name=data["file2"],
            lexical_score=result["lexical_score"],
            syntax_score=result["syntax_score"],
            semantic_score=result["semantic_score"],
            cfg_score=result["cfg_score"],
            pdg_score=result["pdg_score"],
            final_score=result["final_score"],
            verdict=result["verdict"],
        )
        db.add(db_pair)
        
    db.commit()
    db.refresh(db_session)
    return {
        "session": db_session,
        "suspicious_pairs": suspicious_pairs
    }
