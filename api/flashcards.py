from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Flashcard
from database.database import get_db
from utils.utils import generate_example_and_notes, translate_word, get_pos
from api.schemas import PaginatedFlashcardResponse, FlashcardUpdate, FlashcardResponse
from typing import List
from sqlalchemy.future import select
from fastapi import Query
from sqlalchemy import func
import uuid

router = APIRouter()

from fastapi import HTTPException, status

@router.delete("/flashcard/{flashcard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flashcard(flashcard_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Flashcard).where(Flashcard.id == flashcard_id))
    flashcard = result.scalars().first()

    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    await db.delete(flashcard)
    await db.commit()

@router.get("/flashcards", response_model=PaginatedFlashcardResponse)
async def get_flashcards(
    user_id: str = Query(..., min_length=1, description="Authenticated user ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Flashcard).where(Flashcard.user_id == user_id).offset(skip).limit(limit)
    )
    flashcards = result.scalars().all()

    count_result = await db.execute(
        select(func.count()).select_from(Flashcard).where(Flashcard.user_id == user_id)
    )
    total = count_result.scalar_one()

    return {"total": total, "flashcards": flashcards}

@router.put("/flashcard/{flashcard_id}", response_model=FlashcardResponse)
async def update_flashcard(flashcard_id: str, update_data: FlashcardUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Flashcard).where(Flashcard.id == flashcard_id))
    flashcard = result.scalar_one_or_none()

    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(flashcard, field, value)

    await db.commit()
    await db.refresh(flashcard)
    return flashcard

@router.post("/flashcard")
async def generate_flashcard(payload: dict, db: AsyncSession = Depends(get_db)):
    pos = get_pos(payload.word)
    translation = translate_word(payload.word)
    example, notes = generate_example_and_notes(payload.word)
    phonetic = "-".join(payload.word)

    new_flashcard = Flashcard(
        id=str(uuid.uuid4()),
        word=payload.word,
        translation=translation,
        phonetic=phonetic,
        pos=pos,
        example=example,
        notes=notes,
        user_id=payload.userId
    )

    db.add(new_flashcard)
    await db.commit()
    await db.refresh(new_flashcard)
    return new_flashcard