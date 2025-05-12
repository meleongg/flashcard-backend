from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List

from database.database import get_db
from auth.dependencies import get_current_user
from models.quiz import QuizSession, QuizAnswerLog
from api.schemas import UserStatsResponse

router = APIRouter()

@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    # Total quizzes
    quiz_count_result = await db.execute(
        select(func.count()).select_from(QuizSession).where(QuizSession.user_id == user_id)
    )
    total_quizzes = quiz_count_result.scalar_one()

    # Total answers
    answer_count_result = await db.execute(
        select(func.count()).select_from(QuizAnswerLog).join(QuizSession).where(QuizSession.user_id == user_id)
    )
    total_answers = answer_count_result.scalar_one()

    # Correct answers
    correct_count_result = await db.execute(
        select(func.count()).select_from(QuizAnswerLog).join(QuizSession).where(
            QuizSession.user_id == user_id, QuizAnswerLog.is_correct.is_(True)
        )
    )
    correct_answers = correct_count_result.scalar_one()

    # Streak calculation: Count distinct activity dates
    date_result = await db.execute(
        select(func.date_trunc('day', QuizAnswerLog.answered_at))
        .join(QuizSession)
        .where(QuizSession.user_id == user_id)
        .distinct()
    )
    dates = sorted([row[0].date() for row in date_result.all()])
    streak = 0
    today = datetime.utcnow().date()

    # Calculate streak (consecutive days up to today)
    for day_offset in range(len(dates)):
        if (today - timedelta(days=day_offset)) in dates:
            streak += 1
        else:
            break

    return UserStatsResponse(
        total_quizzes=total_quizzes,
        total_answers=total_answers,
        correct_answers=correct_answers,
        accuracy_percent=(correct_answers / total_answers * 100) if total_answers else 0.0,
        streak_days=streak,
        recent_activity=dates[-7:]  # optional: last 7 days
    )