from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import Base  # shared declarative base

class User(Base):
    __tablename__ = "User"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)

    flashcards = relationship(
        "Flashcard",
        back_populates="user",
        cascade="all, delete"
    )
    quiz_sessions = relationship("QuizSession", back_populates="user", cascade="all, delete")