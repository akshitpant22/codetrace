import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class MultiSession(Base):
    """
    Represents a single multi-file analysis session.
    Tracks the overall metadata of the operation.
    """
    __tablename__ = "multi_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()), nullable=False)
    total_files = Column(Integer, nullable=False)
    language = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    pair_results = relationship("MultiPairResult", back_populates="session", cascade="all, delete-orphan")

class MultiPairResult(Base):
    """
    Represents the detailed results of a single pair comparison
    within a broader multi-file analysis session.
    """
    __tablename__ = "multi_pair_results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("multi_sessions.session_id", ondelete="CASCADE"), nullable=False)
    
    file1_name = Column(String, nullable=False)
    file2_name = Column(String, nullable=False)
    lexical_score  = Column(Float, nullable=False)
    syntax_score   = Column(Float, nullable=False)
    semantic_score = Column(Float, nullable=False)
    cfg_score      = Column(Float, nullable=False)
    pdg_score      = Column(Float, nullable=False)
    final_score    = Column(Float, nullable=False)
    verdict        = Column(String, nullable=False)
    session = relationship("MultiSession", back_populates="pair_results")
