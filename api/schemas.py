from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FlashcardUpdate(BaseModel):
    word: Optional[str]
    translation: Optional[str]
    phonetic: Optional[str]
    pos: Optional[str]
    example: Optional[str]
    notes: Optional[str]

    class Config:
        orm_mode = True

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

    class Config:
        orm_mode = True # tells pydantic to accept SQLAlchemy as input

class PaginatedFlashcardResponse(BaseModel):
    total: int
    flashcards: List[FlashcardResponse]