import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.database import engine
from models import Base

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_models())