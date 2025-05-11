import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import text
from database.database import engine
from models import Folder, Flashcard, QuizSession, QuizAnswerLog
from models.base import Base

async def drop_app_models():
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.drop_all(
            bind=sync_conn,
            tables=[
                QuizAnswerLog.__table__,
                QuizSession.__table__,
                Flashcard.__table__,
                Folder.__table__,
            ]
        ))

if __name__ == "__main__":
    asyncio.run(drop_app_models())