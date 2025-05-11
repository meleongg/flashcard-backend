import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.database import engine
from models import Folder, Flashcard, QuizSession, QuizAnswerLog  # ⛔ no User
from models.base import Base

async def init_app_models():
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(
            bind=sync_conn,
            tables=[
                Folder.__table__,
                Flashcard.__table__,
                QuizSession.__table__,
                QuizAnswerLog.__table__,
            ]
        ))

if __name__ == "__main__":
    asyncio.run(init_app_models())