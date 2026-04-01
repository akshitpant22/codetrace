from datetime import datetime
from pydantic import BaseModel, Field


class ResultCreate(BaseModel):
    file1_name:     str   = Field(..., example="student_a.py")
    file2_name:     str   = Field(..., example="student_b.py")
    language:       str   = Field(..., example="python")
    lexical_score:  float = Field(..., ge=0.0, le=1.0, example=0.85)
    syntax_score:   float = Field(..., ge=0.0, le=1.0, example=0.78)
    semantic_score: float = Field(..., ge=0.0, le=1.0, example=0.91)
    final_score:    float = Field(..., ge=0.0, le=1.0, example=0.84)


class ResultResponse(BaseModel):
    id:             int
    file1_name:     str
    file2_name:     str
    language:       str
    lexical_score:  float
    syntax_score:   float
    semantic_score: float
    final_score:    float
    created_at:     datetime

    model_config = {"from_attributes": True}
