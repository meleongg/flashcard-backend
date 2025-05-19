from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, case, distinct
from datetime import datetime, timedelta
from collections import Counter
from database.database import get_db
from auth.dependencies import get_current_user
from models.quiz import QuizSession, QuizAnswerLog
from models.flashcard import Flashcard
from models.review import ReviewEvent, ReviewSession
from api.schemas import UserStatsResponse

router = APIRouter()

@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    quiz_stats = await get_quiz_stats(db, user_id)
    review_stats = await get_review_stats(db, user_id)
    activity_and_streak = await get_activity_and_streak(db, user_id)

    return {
        **quiz_stats,
        **review_stats,
        **activity_and_streak
    }

async def get_quiz_stats(db: AsyncSession, user_id: str):
    quiz_count_result = await db.execute(
        select(func.count()).select_from(QuizSession).where(QuizSession.user_id == user_id)
    )
    total_quizzes = quiz_count_result.scalar_one()

    answer_count_result = await db.execute(
        select(func.count()).select_from(QuizAnswerLog).join(QuizSession).where(QuizSession.user_id == user_id)
    )
    total_answers = answer_count_result.scalar_one()

    correct_count_result = await db.execute(
        select(func.count()).select_from(QuizAnswerLog).join(QuizSession).where(
            QuizSession.user_id == user_id, QuizAnswerLog.is_correct.is_(True)
        )
    )
    correct_answers = correct_count_result.scalar_one()

    accuracy_percent = (correct_answers / total_answers * 100) if total_answers else 0.0

    return {
        "total_quizzes": total_quizzes,
        "total_answers": total_answers,
        "correct_answers": correct_answers,
        "accuracy_percent": accuracy_percent
    }

async def get_review_stats(db: AsyncSession, user_id: str):
    review_sessions_result = await db.execute(
        select(func.count(distinct(ReviewSession.id))).where(ReviewSession.user_id == user_id)
    )
    total_reviews = review_sessions_result.scalar_one_or_none() or 0

    cards_reviewed_result = await db.execute(
        select(func.count(ReviewEvent.id)).where(ReviewEvent.user_id == user_id)
    )
    cards_reviewed = cards_reviewed_result.scalar_one_or_none() or 0

    avg_cards_per_session = cards_reviewed / total_reviews if total_reviews > 0 else 0

    retention_result = await db.execute(
        select(
            func.count(case((ReviewEvent.rating >= 3, 1), else_=None)) * 100.0 /
            func.count(ReviewEvent.id)
        ).where(ReviewEvent.user_id == user_id)
    )
    retention_rate = retention_result.scalar_one_or_none() or 0

    seven_days_ago = datetime.now() - timedelta(days=7)
    result = await db.execute(
        select(
            func.date(ReviewEvent.created_at).label("date"),
            (
                func.count(case((ReviewEvent.rating >= 3, 1), else_=None)) * 100.0 /
                func.count(ReviewEvent.id)
            ).label("rate")
        ).where(
            ReviewEvent.user_id == user_id,
            ReviewEvent.created_at >= seven_days_ago
        ).group_by(func.date(ReviewEvent.created_at)).order_by("date")
    )
    retention_over_time = [
        {"date": str(row.date), "rate": float(row.rate)}
        for row in result.all()
    ]

    interval_bins = [
        (1, "1 day"),
        (3, "2-3 days"),
        (7, "4-7 days"),
        (14, "1-2 weeks"),
        (28, "2-4 weeks"),
        (float('inf'), "1+ month")
    ]

    interval_distribution = []
    for i, (upper, label) in enumerate(interval_bins):
        lower = 0 if i == 0 else interval_bins[i-1][0]
        if i == len(interval_bins) - 1:
            result = await db.execute(
                select(func.count(Flashcard.id)).where(
                    Flashcard.user_id == user_id,
                    Flashcard.interval >= lower
                )
            )
        else:
            result = await db.execute(
                select(func.count(Flashcard.id)).where(
                    Flashcard.user_id == user_id,
                    Flashcard.interval >= lower,
                    Flashcard.interval < upper
                )
            )
        count = result.scalar_one_or_none() or 0
        interval_distribution.append({"interval": label, "count": count})

    return {
        "total_reviews": total_reviews,
        "cards_reviewed": cards_reviewed,
        "avg_cards_per_session": avg_cards_per_session,
        "retention_rate": retention_rate,
        "review_retention_over_time": retention_over_time,
        "interval_distribution": interval_distribution
    }

async def get_activity_and_streak(db: AsyncSession, user_id: str):
    date_result = await db.execute(
        select(func.date_trunc('day', QuizAnswerLog.answered_at))
        .join(QuizSession)
        .where(QuizSession.user_id == user_id)
        .distinct()
    )
    dates = sorted([row[0].date() for row in date_result.all()])
    streak = 0
    today = datetime.utcnow().date()
    for day_offset in range(len(dates)):
        if (today - timedelta(days=day_offset)) in dates:
            streak += 1
        else:
            break

    return {
        "streak_days": streak,
        "recent_activity": dates[-7:]
    }

@router.get("/stats/pos-distribution")
async def get_pos_distribution(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    result = await db.execute(
        select(Flashcard.pos).where(Flashcard.user_id == user_id)
    )
    pos_tags = result.scalars().all()

    # Filter out null or empty
    pos_tags = [tag for tag in pos_tags if tag]
    return Counter(pos_tags)