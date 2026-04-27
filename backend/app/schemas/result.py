from datetime import datetime
from pydantic import BaseModel, Field


class ResultCreate(BaseModel):
    file1_name:     str   = Field(..., example="student_a.py")
    file2_name:     str   = Field(..., example="student_b.py")
    language:       str   = Field(..., example="python")
    lexical_score:  float = Field(..., ge=0.0, le=100.0, example=85.0)
    syntax_score:   float = Field(..., ge=0.0, le=100.0, example=78.0)
    semantic_score: float = Field(..., ge=0.0, le=100.0, example=91.0)
    cfg_score:      float = Field(..., ge=0.0, le=100.0, example=88.5)
    pdg_score:      float = Field(..., ge=0.0, le=100.0, example=90.2)
    final_score:    float = Field(..., ge=0.0, le=100.0, example=84.0)
    verdict:        str   = Field(..., example="Plagiarized")


class ResultResponse(BaseModel):
    id:             int
    file1_name:     str
    file2_name:     str
    language:       str
    lexical_score:  float
    syntax_score:   float
    semantic_score: float
    cfg_score:      float
    pdg_score:      float
    final_score:    float
    verdict:        str
    created_at:     datetime

    model_config = {"from_attributes": True}
