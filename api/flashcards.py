from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Flashcard
from database.database import get_db
from utils.utils import generate_example_and_notes, translate_word, get_pos
from api.schemas import PaginatedFlashcardResponse
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
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    db: AsyncSession = Depends(get_db),
):
    # Fetch paginated flashcards
    result = await db.execute(
        select(Flashcard).where(Flashcard.user_id == user_id).offset(skip).limit(limit)
    )
    flashcards = result.scalars().all()

    # Fetch total count
    count_result = await db.execute(
        select(func.count()).select_from(Flashcard).where(Flashcard.user_id == user_id)
    )
    total = count_result.scalar_one()

    return {"total": total, "flashcards": flashcards}


@router.post("/flashcard")
async def generate_flashcard(payload: dict, db: AsyncSession = Depends(get_db)):
    word = payload.get("word", "")
    user_id = payload.get("userId")

    if not word or not user_id:
        return {"error": "Missing word or userId"}

    pos = get_pos(word)
    translation = translate_word(word)
    example, notes = generate_example_and_notes(word)
    phonetic = "-".join(word)

    new_flashcard = Flashcard(
        id=str(uuid.uuid4()),
        word=word,
        translation=translation,
        phonetic=phonetic,
        pos=pos,
        example=example,
        notes=notes,
        user_id=user_id
    )

    db.add(new_flashcard)
    await db.commit()
    await db.refresh(new_flashcard)

    return {
        "word": word,
        "translation": translation,
        "phonetic": phonetic,
        "pos": pos,
        "example": example,
        "notes": notes
    }