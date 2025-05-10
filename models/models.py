from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# defines database schema in Python using SQLAlchemy ORM (like backend prisma.schema)

Base = declarative_base()

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

class Flashcard(Base):
  __tablename__ = "Flashcard"

  id = Column(String, primary_key=True, index=True)
  word = Column(String, nullable=False)
  translation = Column(String, nullable=False)
  phonetic = Column(String, nullable=False)
  pos = Column(String, nullable=True)
  example = Column(Text, nullable=False)
  notes = Column(Text, nullable=False)
  user_id = Column("userId", String, ForeignKey("User.id"), nullable=False)
  user = relationship("User", back_populates="flashcards")
  created_at = Column("createdAt", DateTime, default=lambda: datetime.utcnow())

  folder_id = Column(String, ForeignKey("Folder.id", ondelete="SET NULL"), nullable=True)
  folder = relationship("Folder", back_populates="flashcards")

class User(Base):
    __tablename__ = "User"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)

    flashcards = relationship("Flashcard", back_populates="user")