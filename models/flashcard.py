from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base  # Import shared declarative_base

class Flashcard(Base):
    __tablename__ = "Flashcard"

    id = Column(String, primary_key=True, index=True)
    word = Column(String, nullable=False)
    translation = Column(String, nullable=False)
    phonetic = Column(String)
    pos = Column(String)
    example = Column(Text)
    notes = Column(Text)
    source_lang = Column(String, nullable=False, default="en")
    target_lang = Column(String, nullable=False, default="zh")
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(String, ForeignKey("User.id"), nullable=False)
    folder_id = Column(String, ForeignKey("Folder.id"), nullable=True)

    folder = relationship("Folder", back_populates="flashcards")
    user = relationship("User", back_populates="flashcards")