from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

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