from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from random import shuffle
from typing import List
import uuid
from datetime import datetime

from database.database import get_db
from auth.dependencies import get_current_user
from models.quiz import QuizSession, QuizAnswerLog
from models.flashcard import Flashcard
from api.schemas import (
    FlashcardResponse,
    QuizSessionCreate,
    QuizSessionResponse,
    QuizAnswerLogCreate,
    QuizAnswerLogResponse
)

router = APIRouter()

@router.get("/quiz", response_model=List[FlashcardResponse])
async def get_quiz_cards(
    folder_id: str = Query(None),
    count: int = Query(10, ge=1, le=100),
    include_reverse: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    query = select(Flashcard).where(Flashcard.user_id == user_id)

    if folder_id and folder_id != "all":
        query = query.where(Flashcard.folder_id == folder_id)

    result = await db.execute(query)
    cards = result.scalars().all()

    if not cards:
        raise HTTPException(status_code=404, detail="No flashcards found.")

    shuffle(cards)
    selected = cards[:count]

    # Reverse mode: test translation → word
    if include_reverse:
        reversed_cards = [
            FlashcardResponse(
                id=c.id,
                word=c.translation,
                translation=c.word,
                phonetic=c.phonetic,
                pos=c.pos,
                example=c.example,
                notes=c.notes,
                folder_id=c.folder_id,
                user_id=c.user_id,
                source_lang=c.target_lang,
                target_lang=c.source_lang,
            )
            for c in selected
        ]
        selected += reversed_cards
        shuffle(selected)

    return selected

# Create a new quiz session
@router.post("/quiz/session", response_model=QuizSessionResponse)
async def create_quiz_session(
    payload: QuizSessionCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    session_id = str(uuid.uuid4())
    new_session = QuizSession(
        id=session_id,
        user_id=user_id,
        folder_id=payload.folder_id,
        include_reverse=payload.include_reverse,
        card_count=payload.card_count,
        created_at=datetime.utcnow(),
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session

# Submit an answer to a quiz card
@router.post("/quiz/session/answer", response_model=QuizAnswerLogResponse)
async def log_quiz_answer(
    payload: QuizAnswerLogCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    # Validate that session belongs to user
    session_query = await db.execute(
        select(QuizSession).where(QuizSession.id == payload.session_id, QuizSession.user_id == user_id)
    )
    session = session_query.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Quiz session not found")

    new_log = QuizAnswerLog(
        id=str(uuid.uuid4()),
        session_id=payload.session_id,
        flashcard_id=payload.flashcard_id,
        is_correct=payload.is_correct,
        answered_at=datetime.utcnow(),
    )
    db.add(new_log)
    await db.commit()
    await db.refresh(new_log)
    return new_log

# Get all past sessions for the current user
@router.get("/quiz/sessions", response_model=List[QuizSessionResponse])
async def get_all_sessions(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    result = await db.execute(
        select(QuizSession).where(QuizSession.user_id == user_id).order_by(QuizSession.created_at.desc())
    )
    sessions = result.scalars().all()
    return sessions

# Get a single quiz session and its logs
@router.get("/quiz/session/{session_id}", response_model=QuizSessionResponse)
async def get_session_by_id(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    result = await db.execute(
        select(QuizSession).where(QuizSession.id == session_id, QuizSession.user_id == user_id)
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Manually load answers
    answers_result = await db.execute(
        select(QuizAnswerLog).where(QuizAnswerLog.session_id == session.id)
    )
    session.answers = answers_result.scalars().all()
    return session