from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class QuizSession(Base):
    __tablename__ = "QuizSession"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("User.id"), nullable=False)
    folder_id = Column(String, ForeignKey("Folder.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    include_reverse = Column(Boolean, default=False)
    card_count = Column(Integer)

    user = relationship("User", back_populates="quiz_sessions")
    folder = relationship("Folder")
    answers = relationship(
        "QuizAnswerLog",
        back_populates="session",
        cascade="all, delete",
        lazy="selectin", # make them loaded on request (instead of lazily)
    )


class QuizAnswerLog(Base):
    __tablename__ = "QuizAnswerLog"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("QuizSession.id"), nullable=False)
    flashcard_id = Column(String, ForeignKey("Flashcard.id"), nullable=False)
    is_correct = Column(Boolean, default=False)
    answered_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("QuizSession", back_populates="answers")
    flashcard = relationship("Flashcard")