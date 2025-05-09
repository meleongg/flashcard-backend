import sys
import os

# Append the parent directory (project root) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from models.models import Flashcard
import asyncio
from database.database import engine
import os
from dotenv import load_dotenv

load_dotenv()
user_id = os.getenv("SEED_USER_ID")

AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

sample_flashcards = [
    {
        "word": "hello",
        "translation": "你好",
        "phonetic": "h-e-l-l-o",
        "pos": "INTJ",
        "example": "Hello, how are you?",
        "notes": "Used as a greeting."
    },
    {
        "word": "eat",
        "translation": "吃",
        "phonetic": "e-a-t",
        "pos": "VERB",
        "example": "I eat lunch at noon.",
        "notes": "Verb describing the act of consuming food."
    },
    {
        "word": "fast",
        "translation": "快",
        "phonetic": "f-a-s-t",
        "pos": "ADJ",
        "example": "The car is very fast.",
        "notes": "Adjective describing speed."
    },
    {
        "word": "beautiful",
        "translation": "美丽",
        "phonetic": "b-e-a-u-t-i-f-u-l",
        "pos": "ADJ",
        "example": "She has a beautiful voice.",
        "notes": "Describes something pleasing to the senses."
    },
    {
        "word": "where",
        "translation": "哪里",
        "phonetic": "w-h-e-r-e",
        "pos": "ADV",
        "example": "Where are you going?",
        "notes": "Used to ask about a place."
    },
]

async def seed_flashcards():
    async with AsyncSessionLocal() as session:
        for data in sample_flashcards:
            flashcard = Flashcard(
                id=str(uuid.uuid4()),
                word=data["word"],
                translation=data["translation"],
                phonetic=data["phonetic"],
                pos=data["pos"],
                example=data["example"],
                notes=data["notes"],
                user_id=user_id,
                created_at=datetime.utcnow()
            )
            session.add(flashcard)
        await session.commit()
        print("✅ Seeded flashcards!")

async def clear_flashcards():
    async with AsyncSessionLocal() as session:
        await session.execute(text('DELETE FROM "Flashcard"'))
        await session.commit()
        print("🧹 Cleared flashcards.")

# Uncomment the line you want to run:
asyncio.run(seed_flashcards())
# asyncio.run(clear_flashcards())