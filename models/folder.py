from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Folder(Base):
    __tablename__ = "Folder"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    user_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    flashcards = relationship(
        "Flashcard",
        back_populates="folder",
        passive_deletes=True,
    )