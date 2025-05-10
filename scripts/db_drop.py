import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.models import Base
from database.database import engine

async def drop_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

if __name__ == "__main__":
    asyncio.run(drop_models())