from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.database import get_db
from auth.dependencies import get_current_user
from models.review import ReviewSession, ReviewEvent
from models.flashcard import Flashcard
from api.schemas import FlashcardResponse
from api.flashcards import to_flashcard_response
from datetime import date, timedelta
import uuid

router = APIRouter()

@router.post("/review-sessions/start")
async def start_review_session(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    session = ReviewSession(id=str(uuid.uuid4()), user_id=user_id)
    db.add(session)
    await db.commit()
    return {"session_id": session.id}

@router.post("/review-sessions/{session_id}/review", response_model=FlashcardResponse)
async def review_flashcard_with_session(
    session_id: str,
    flashcard_id: str = Body(..., embed=True),
    quality: int = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    if quality < 0 or quality > 5:
        raise HTTPException(status_code=400, detail="Quality must be between 0 and 5")

    session_check = await db.execute(
        select(ReviewSession).where(ReviewSession.id == session_id, ReviewSession.user_id == user_id)
    )
    session = session_check.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Invalid or expired review session.")

    result = await db.execute(
        select(Flashcard).where(Flashcard.id == flashcard_id, Flashcard.user_id == user_id)
    )
    flashcard = result.scalar_one_or_none()
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

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

@router.get("/review-sessions/{session_id}/summary")
async def get_review_session_summary(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    session_check = await db.execute(
        select(ReviewSession).where(ReviewSession.id == session_id, ReviewSession.user_id == user_id)
    )
    session = session_check.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Review session not found")

    event_query = await db.execute(
        select(ReviewEvent.rating).where(ReviewEvent.session_id == session_id)
    )
    ratings = [row[0] for row in event_query.fetchall()]

    if not ratings:
        return {
            "session_id": session_id,
            "user_id": user_id,
            "total_cards": 0,
            "average_rating": 0.0,
            "ratings_breakdown": {str(i): 0 for i in range(6)},
            "reviewed_at": session.created_at
        }

    total = len(ratings)
    avg = sum(ratings) / total
    breakdown = {str(i): ratings.count(i) for i in range(6)}

    return {
        "session_id": session_id,
        "user_id": user_id,
        "total_cards": total,
        "average_rating": round(avg, 2),
        "ratings_breakdown": breakdown,
        "reviewed_at": session.created_at
    }