from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from models import Flashcard, Folder
from database.database import get_db
from utils.utils import generate_flashcard_with_gpt, get_phonetic, get_pos, detect_language
from api.schemas import (
  PaginatedFlashcardResponse,
  FlashcardUpdate,
  FlashcardSubmit,
  FlashcardResponse,
  FlashcardCreate,
  FlashcardFolderUpdate,
  FlashcardPreview,
  SpacedRepetitionMetadata,
  FlashcardReviewPreview
)
from auth.dependencies import get_current_user
from datetime import date, timedelta
from typing import List
import uuid
import os

SECRET_KEY = os.getenv("NEXTAUTH_SECRET")
ALGORITHM = "HS256"

router = APIRouter()

def to_flashcard_response(flashcard: Flashcard) -> FlashcardResponse:
  return FlashcardResponse(
      id=flashcard.id,
      word=flashcard.word,
      translation=flashcard.translation,
      phonetic=flashcard.phonetic,
      pos=flashcard.pos,
      example=flashcard.example,
      notes=flashcard.notes,
      source_lang=flashcard.source_lang,
      target_lang=flashcard.target_lang,
      user_id=flashcard.user_id,
      created_at=flashcard.created_at,
      folder_id=flashcard.folder_id,
      spaced_repetition=SpacedRepetitionMetadata(
          review_count=flashcard.review_count,
          interval=flashcard.interval,
          ease_factor=flashcard.ease_factor,
          last_reviewed=flashcard.last_reviewed,
          next_review_date=flashcard.next_review_date
      )
  )

@router.delete("/flashcard/{flashcard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flashcard(
    flashcard_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    result = await db.execute(select(Flashcard).where(
        Flashcard.id == flashcard_id, Flashcard.user_id == user_id
    ))
    flashcard = result.scalars().first()

    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    await db.delete(flashcard)
    await db.commit()

@router.get("/flashcards", response_model=PaginatedFlashcardResponse)
async def get_flashcards(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    folder_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    base_query = select(Flashcard).where(Flashcard.user_id == user_id)
    count_query = select(func.count()).select_from(Flashcard).where(Flashcard.user_id == user_id)

    if folder_id:
        base_query = base_query.where(Flashcard.folder_id == folder_id)
        count_query = count_query.where(Flashcard.folder_id == folder_id)

    result = await db.execute(base_query.offset(skip).limit(limit))
    flashcards = result.scalars().all()

    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    return {"total": total, "flashcards": [to_flashcard_response(f) for f in flashcards]}


@router.get("/flashcard/{flashcard_id}", response_model=FlashcardResponse)
async def get_flashcard_detail(
    flashcard_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    result = await db.execute(
        select(Flashcard).where(Flashcard.id == flashcard_id, Flashcard.user_id == user_id)
    )
    flashcard = result.scalars().first()

    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    return to_flashcard_response(flashcard)

@router.post("/flashcard", response_model=FlashcardResponse)
async def save_flashcard(
    flashcard_data: FlashcardSubmit,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    word = flashcard_data.word.strip()
    if not word:
        raise HTTPException(status_code=400, detail="Missing word")

    new_flashcard = Flashcard(
        id=str(uuid.uuid4()),
        word=word,
        translation=flashcard_data.translation,
        phonetic=flashcard_data.phonetic,
        pos=flashcard_data.pos,
        example=flashcard_data.example,
        notes=flashcard_data.notes,
        source_lang=flashcard_data.source_lang,
        target_lang=flashcard_data.target_lang,
        folder_id=flashcard_data.folder_id,
        user_id=user_id,
    )

    db.add(new_flashcard)
    await db.commit()
    await db.refresh(new_flashcard)
    return to_flashcard_response(new_flashcard)

@router.put("/flashcard/{flashcard_id}", response_model=FlashcardResponse)
async def update_flashcard(
    flashcard_id: str,
    update_data: FlashcardUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    result = await db.execute(select(Flashcard).where(
        Flashcard.id == flashcard_id, Flashcard.user_id == user_id
    ))
    flashcard = result.scalar_one_or_none()

    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(flashcard, field, value)

    await db.commit()
    await db.refresh(flashcard)
    return to_flashcard_response(flashcard)

@router.put("/flashcard/{flashcard_id}/folder", response_model=FlashcardResponse)
async def assign_flashcard_to_folder(
    flashcard_id: str,
    folder_update: FlashcardFolderUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    result = await db.execute(
        select(Flashcard).where(Flashcard.id == flashcard_id, Flashcard.user_id == user_id)
    )
    flashcard = result.scalars().first()
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    if folder_update.folder_id:
        folder_result = await db.execute(
            select(Folder).where(Folder.id == folder_update.folder_id, Folder.user_id == user_id)
        )
        folder = folder_result.scalars().first()
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")

    flashcard.folder_id = folder_update.folder_id
    await db.commit()
    await db.refresh(flashcard)
    return to_flashcard_response(flashcard)

@router.post("/flashcard-preview", response_model=FlashcardPreview)
async def preview_flashcard(
    payload: FlashcardCreate,
    user_id: str = Depends(get_current_user)
):
    word = payload.word.strip()
    source_lang = payload.source_lang or "en"
    target_lang = payload.target_lang or "zh"

    if not word:
        raise HTTPException(status_code=400, detail="Word is required")

    # Auto-detect source language if needed
    if source_lang == "auto":
        source_lang = detect_language(word)

    if target_lang == "auto":
        target_lang = "zh" if source_lang == "en" else "en"

    # ✨ GPT: Combine translation, example, and note generation
    translation, example, notes = generate_flashcard_with_gpt(word, source_lang, target_lang)

    return FlashcardPreview(
        word=word,
        translation=translation,
        phonetic=get_phonetic(word, lang=source_lang),
        pos=get_pos(word, lang=source_lang),
        example=example,
        notes=notes,
        source_lang=source_lang,
        target_lang=target_lang
    )

@router.get("/flashcard/{flashcard_id}", response_model=FlashcardResponse)
async def get_flashcard_detail(
    flashcard_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    result = await db.execute(
        select(Flashcard).where(Flashcard.id == flashcard_id, Flashcard.user_id == user_id)
    )
    flashcard = result.scalars().first()

    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    return to_flashcard_response(flashcard)

@router.get("/flashcards/review", response_model=List[FlashcardResponse])
async def get_due_flashcards(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    today = date.today()
    result = await db.execute(
        select(Flashcard)
        .where(Flashcard.user_id == user_id)
        .where(Flashcard.next_review_date <= today)
        .order_by(Flashcard.next_review_date.asc())
    )
    flashcards = result.scalars().all()
    return [to_flashcard_response(f) for f in flashcards]

@router.post("/flashcards/{flashcard_id}/review", response_model=FlashcardResponse)
async def review_flashcard(
    flashcard_id: str,
    quality: int = Body(..., embed=True),
    session_id: str = Body(..., embed=True),  # New: require session ID
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    from models.review import ReviewEvent, ReviewSession

    if quality < 0 or quality > 5:
        raise HTTPException(status_code=400, detail="Quality must be between 0 and 5")

    # Validate session
    session_check = await db.execute(
        select(ReviewSession).where(ReviewSession.id == session_id, ReviewSession.user_id == user_id)
    )
    session = session_check.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Invalid or expired review session.")

    # Fetch flashcard
    result = await db.execute(
        select(Flashcard)
        .where(Flashcard.id == flashcard_id)
        .where(Flashcard.user_id == user_id)
    )
    flashcard = result.scalar_one_or_none()
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    # SM-2 Logic
    if quality < 3:
        flashcard.interval = 1
        flashcard.review_count = 0
    else:
        flashcard.review_count += 1
        if flashcard.review_count == 1:
            flashcard.interval = 1
        elif flashcard.review_count == 2:
            flashcard.interval = 6
        else:
            flashcard.interval = int(flashcard.interval * flashcard.ease_factor)
        flashcard.ease_factor = max(1.3, flashcard.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

    flashcard.last_reviewed = date.today()
    flashcard.next_review_date = flashcard.last_reviewed + timedelta(days=flashcard.interval)

    # Record ReviewEvent
    review_event = ReviewEvent(
        id=str(uuid.uuid4()),
        session_id=session.id,
        user_id=user_id,
        flashcard_id=flashcard.id,
        rating=quality
    )
    db.add(review_event)

    await db.commit()
    await db.refresh(flashcard)
    return to_flashcard_response(flashcard)

@router.get("/flashcards/review/preview", response_model=List[FlashcardReviewPreview])
async def preview_upcoming_reviews(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    result = await db.execute(
        select(Flashcard)
        .where(Flashcard.user_id == user_id)
        .where(Flashcard.next_review_date.isnot(None))
        .order_by(Flashcard.next_review_date.asc())
        .limit(limit)
    )
    flashcards = result.scalars().all()

    return [
        FlashcardReviewPreview(
            id=f.id,
            word=f.word,
            translation=f.translation,
            phonetic=f.phonetic,
            pos=f.pos,
            example=f.example,
            next_review_date=f.next_review_date,
            interval=f.interval
        )
        for f in flashcards
    ]