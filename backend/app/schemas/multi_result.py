from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class MultiPairResultResponse(BaseModel):
    """
    Schema for an individual pairwise comparison within a multi-file session.
    """
    id:             int
    session_id:     str
    file1_name:     str
    file2_name:     str
    
    lexical_score:  float
    syntax_score:   float
    semantic_score: float
    cfg_score:      float
    pdg_score:      float
    
    final_score:    float
    verdict:        str

    model_config = {"from_attributes": True}


class MultiSessionResponse(BaseModel):
    """
    Schema for the parent multi-file session metadata, including all pairs.
    """
    id:             int
    session_id:     str
    total_files:    int
    language:       str
    created_at:     datetime
    
    # Automatically populated via SQLAlchemy relationship
    pair_results:   List[MultiPairResultResponse] = []

    model_config = {"from_attributes": True}


class SuspiciousPair(BaseModel):
    """
    Schema to structure the ranked list of suspicious pairs.
    """
    pair:        str
    file1:       str
    file2:       str
    final_score: float
    verdict:     str
    details:     Dict[str, Any]


class MultiAnalysisResponse(BaseModel):
    """
    The final complete payload returned from the /api/multi-analyze endpoint.
    """
    session:          MultiSessionResponse
    suspicious_pairs: List[SuspiciousPair]
