from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class FlashcardFolderUpdate(BaseModel):
    folder_id: str | None  # allow null to remove from folder
class FlashcardCreate(BaseModel):
    word: str = Field(..., min_length=1, max_length=100)
    userId: str = Field(..., min_length=5)

class FlashcardPreview(BaseModel):
    word: str
    translation: str
    phonetic: str
    pos: Optional[str]
    example: str
    notes: str

class FlashcardUpdate(BaseModel):
    word: Optional[str] = Field(None, min_length=1, max_length=100)
    translation: Optional[str] = Field(None, max_length=100)
    phonetic: Optional[str] = Field(None, max_length=100)
    pos: Optional[str] = Field(None, max_length=50)
    example: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=200)
    folder_id: Optional[str] = None

class FlashcardResponse(BaseModel):
    id: str
    word: str
    translation: str
    phonetic: str
    pos: Optional[str] = None
    example: str
    notes: str
    user_id: str
    created_at: datetime
    folder_id: Optional[str] = None

    class Config:
        orm_mode = True # tells pydantic to accept SQLAlchemy as input

class PaginatedFlashcardResponse(BaseModel):
    total: int
    flashcards: List[FlashcardResponse]

class FolderCreate(BaseModel):
    name: str

class FolderResponse(BaseModel):
    id: str
    name: str
    user_id: str
    created_at: datetime

    class Config:
        orm_mode = True