from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.result import Result
from app.models.user import User
from app.schemas.result import ResultResponse

router = APIRouter(prefix="/api", tags=["history"])

@router.get("/history", response_model=List[ResultResponse])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch all previous analysis results.
    The response automatically includes the new fields (cfg_score, pdg_score, verdict)
    thanks to the updated ResultResponse schema and Result database model.
    """
    results = db.query(Result).order_by(Result.created_at.desc()).all()
    return results

@router.delete("/history/all")
def clear_all_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Clear all records from the results table.
    """
    db.query(Result).delete()
    db.commit()
    return {"message": "All history cleared"}

@router.delete("/history/{id}")
def delete_history_record(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a specific analysis result by its ID.
    """
    result = db.query(Result).filter(Result.id == id).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found"
        )
    
    db.delete(result)
    db.commit()
    return {"message": "Record deleted successfully"}
