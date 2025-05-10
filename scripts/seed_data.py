import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from models.models import Flashcard, Folder
import asyncio
from database.database import engine
from dotenv import load_dotenv

load_dotenv()
user_id = os.getenv("SEED_USER_ID")

AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

sample_folders = [
    {"name": "Basics"},
    {"name": "Verbs"},
    {"name": "Adjectives"},
]

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

async def seed_data():
    async with AsyncSessionLocal() as session:
        # Seed folders
        folders = []
        for folder_data in sample_folders:
            folder = Folder(
                id=str(uuid.uuid4()),
                name=folder_data["name"],
                user_id=user_id,
                created_at=datetime.utcnow()  # ✅ Include created_at
            )
            session.add(folder)
            folders.append(folder)
        await session.flush()  # Ensure folder IDs are available

        # Seed flashcards (assign all to the first folder for simplicity)
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
                folder_id=folders[0].id,
                created_at=datetime.utcnow()
            )
            session.add(flashcard)

        await session.commit()
        print("✅ Seeded folders and flashcards!")

async def clear_data():
    async with AsyncSessionLocal() as session:
        await session.execute(text('DELETE FROM "Flashcard"'))
        await session.execute(text('DELETE FROM "Folder"'))
        await session.commit()
        print("🧹 Cleared all flashcards and folders.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["seed", "clear"], help="Choose to seed or clear the database.")
    args = parser.parse_args()

    if args.action == "seed":
        asyncio.run(seed_data())
    elif args.action == "clear":
        asyncio.run(clear_data())