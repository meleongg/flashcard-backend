from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = "User"

    id = Column(String, primary_key=True)
    # Don't redefine all fields; SQLAlchemy can just use this for relationships

    flashcards = relationship("Flashcard", back_populates="user", cascade="all, delete")
    quiz_sessions = relationship("QuizSession", back_populates="user", cascade="all, delete")