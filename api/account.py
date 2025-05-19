from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database.database import get_db
from auth.dependencies import get_current_user

router = APIRouter()

@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    try:
        # Delete review data first (due to foreign key constraints)
        await db.execute(text('DELETE FROM "ReviewEvent" WHERE user_id = :user_id'), {"user_id": user_id})
        await db.execute(text('DELETE FROM "ReviewSession" WHERE user_id = :user_id'), {"user_id": user_id})

        # Delete quiz data (answers must be removed before sessions)
        await db.execute(text(
            'DELETE FROM "QuizAnswerLog" WHERE session_id IN (SELECT id FROM "QuizSession" WHERE user_id = :user_id)'
        ), {"user_id": user_id})
        await db.execute(text('DELETE FROM "QuizSession" WHERE user_id = :user_id'), {"user_id": user_id})

        # Delete flashcards and folders
        await db.execute(text('DELETE FROM "Flashcard" WHERE user_id = :user_id'), {"user_id": user_id})
        await db.execute(text('DELETE FROM "Folder" WHERE user_id = :user_id'), {"user_id": user_id})

        # Delete user settings
        await db.execute(text('DELETE FROM "UserSettings" WHERE user_id = :user_id'), {"user_id": user_id})

        # Delete the user record itself
        await db.execute(text('DELETE FROM "User" WHERE id = :user_id'), {"user_id": user_id})

        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete account: {str(e)}")