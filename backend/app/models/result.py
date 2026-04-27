from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)

    file1_name = Column(String, nullable=False)
    file2_name = Column(String, nullable=False)
    language   = Column(String, nullable=False)

    lexical_score  = Column(Float, nullable=False)
    syntax_score   = Column(Float, nullable=False)
    semantic_score = Column(Float, nullable=False)
    cfg_score      = Column(Float, nullable=False)
    pdg_score      = Column(Float, nullable=False)
    final_score    = Column(Float, nullable=False)
    verdict        = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
