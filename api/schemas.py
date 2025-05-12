from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class UserRead(BaseModel):
    id: str
    email: Optional[str] = None

    class Config:
        orm_mode = True
class FlashcardData(BaseModel):
    word: str
    translation: str
    phonetic: str
    pos: str
    example: str
    notes: str
    source_lang: Optional[str] = "en"
    target_lang: Optional[str] = "zh"
class FlashcardFolderUpdate(BaseModel):
    folder_id: str | None  # allow null to remove from folder

class FlashcardCreate(BaseModel):
    word: str
    folder_id: Optional[str] = None
    source_lang: str = "en"
    target_lang: str = "zh"

class FlashcardResponse(FlashcardCreate):
    id: str
    translation: str
    phonetic: str
    pos: str
    example: str
    notes: str

    class Config:
        orm_mode = True

class FlashcardPreview(BaseModel):
    word: str
    translation: str
    phonetic: str
    pos: str
    example: str
    notes: str
    source_lang: str
    target_lang: str

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
    source_lang: str
    target_lang: str
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

class QuizAnswerLogBase(BaseModel):
    flashcard_id: str
    is_correct: bool

class QuizAnswerLogCreate(QuizAnswerLogBase):
    session_id: str

class QuizAnswerLogResponse(QuizAnswerLogBase):
    id: str
    answered_at: datetime

    class Config:
        orm_mode = True

class QuizSessionBase(BaseModel):
    folder_id: Optional[str] = None
    include_reverse: bool = False
    card_count: int = 10

class QuizSessionCreate(QuizSessionBase):
    pass

class QuizSessionResponse(QuizSessionBase):
    id: str
    user_id: str
    created_at: datetime
    answers: List[QuizAnswerLogResponse] = []

    class Config:
        orm_mode = True

class UserStatsResponse(BaseModel):
    total_quizzes: int
    total_answers: int
    correct_answers: int
    accuracy_percent: float
    streak_days: int
    recent_activity: List[datetime]

    class Config:
        orm_mode = True

class UserSettingsResponse(BaseModel):
    default_source_lang: str
    default_target_lang: str
    default_quiz_length: int
    auto_tts: bool
    reverse_quiz_default: bool
    dark_mode: bool
    daily_learning_goal: int

    class Config:
        orm_mode = True

class UserSettingsUpdate(BaseModel):
    default_source_lang: Optional[str]
    default_target_lang: Optional[str]
    default_quiz_length: Optional[int]
    auto_tts: Optional[bool]
    reverse_quiz_default: Optional[bool]
    dark_mode: Optional[bool]
    daily_learning_goal: Optional[int]