from sqlalchemy import Column, String, ForeignKey, DateTime, SmallInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class ReviewSession(Base):
    __tablename__ = "ReviewSession"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("User.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="review_sessions")
    events = relationship("ReviewEvent", back_populates="session", cascade="all, delete")


class ReviewEvent(Base):
    __tablename__ = "ReviewEvent"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("ReviewSession.id"), nullable=False)
    user_id = Column(String, ForeignKey("User.id"), nullable=False)
    flashcard_id = Column(String, ForeignKey("Flashcard.id"), nullable=False)
    rating = Column(SmallInteger, nullable=False)  # 0–5 scale
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ReviewSession", back_populates="events")
    flashcard = relationship("Flashcard")
    user = relationship("User")