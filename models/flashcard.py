from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Float, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base  # SQLAlchemy declarative_base

class Flashcard(Base):
    __tablename__ = "Flashcard"

    # Core flashcard content
    id = Column(String, primary_key=True, index=True)
    word = Column(String, nullable=False)
    translation = Column(String, nullable=False)
    phonetic = Column(String)
    pos = Column(String)
    example = Column(Text)
    notes = Column(Text)

    # Language metadata
    source_lang = Column(String, nullable=False, default="en")
    target_lang = Column(String, nullable=False, default="zh")

    # Spaced repetition metadata (SM-2)
    review_count = Column(Integer, default=0)
    last_reviewed = Column(Date, nullable=True)
    next_review_date = Column(Date, nullable=True)
    ease_factor = Column(Float, default=2.5)  # SM-2 default ease factor
    interval = Column(Integer, default=0)     # Days until next review

    # Ownership and structure
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, ForeignKey("User.id"), nullable=False)
    folder_id = Column(String, ForeignKey("Folder.id"), nullable=True)

    # Relationships
    folder = relationship("Folder", back_populates="flashcards")
    user = relationship("User", back_populates="flashcards")