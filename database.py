from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# setup connection between FastAPI and NeonDB using SQLAlchemy

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True, connect_args={"ssl": True}) # create connection engine to db
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False) # creates session factory for access to the database

# FastAPI dependency that can be used in route handlers
# ensures fresh DB session per request & auto-closing when finished
async def get_db():
  async with AsyncSessionLocal() as session:
    yield session