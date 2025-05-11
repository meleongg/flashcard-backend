from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.database import get_db
from auth.dependencies import get_current_user
from models.models import Flashcard
from api.schemas import FlashcardResponse
from random import shuffle
from typing import List

router = APIRouter()

@router.get("/quiz", response_model=List[FlashcardResponse])
async def get_quiz_cards(
    folder_id: str = Query(None),
    count: int = Query(10),
    include_reverse: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    query = select(Flashcard).where(Flashcard.user_id == user_id)
    if folder_id and folder_id != "all":
        query = query.where(Flashcard.folder_id == folder_id)

    result = await db.execute(query)
    cards = result.scalars().all()
    shuffle(cards)
    selected = cards[:count]

    # Handle reverse mode
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