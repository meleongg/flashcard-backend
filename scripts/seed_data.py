import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
import uuid
import asyncio
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv
from datetime import datetime, timedelta, date
from database.database import engine
from models import Flashcard, Folder, UserSettings
from models.quiz import QuizSession, QuizAnswerLog
from models.review import ReviewSession, ReviewEvent

load_dotenv(override=True)
user_id = os.getenv("SEED_USER_ID")

if not user_id:
    raise ValueError("⚠️ SEED_USER_ID not found in environment.")

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
        "notes": "Used as a greeting.",
        "source_lang": "en",
        "target_lang": "zh",
    },
    {
        "word": "吃",
        "translation": "eat",
        "phonetic": "chī",
        "pos": "VERB",
        "example": "我每天中午吃饭。",
        "notes": "动词，描述吃东西的动作。",
        "source_lang": "zh",
        "target_lang": "en",
    },
    {
        "word": "fast",
        "translation": "快",
        "phonetic": "f-a-s-t",
        "pos": "ADJ",
        "example": "The car is very fast.",
        "notes": "Adjective describing speed.",
        "source_lang": "en",
        "target_lang": "zh",
    },
    {
        "word": "美丽",
        "translation": "beautiful",
        "phonetic": "měi lì",
        "pos": "ADJ",
        "example": "她有一副美丽的嗓音。",
        "notes": "形容令人愉悦的事物。",
        "source_lang": "zh",
        "target_lang": "en",
    },
    {
        "word": "where",
        "translation": "哪里",
        "phonetic": "w-h-e-r-e",
        "pos": "ADV",
        "example": "Where are you going?",
        "notes": "Used to ask about a place.",
        "source_lang": "en",
        "target_lang": "zh",
    },
]

async def seed_data():
    async with AsyncSessionLocal() as session:
        # ✅ Create default settings for the user
        settings = UserSettings(
            user_id=user_id,
            default_source_lang="en",
            default_target_lang="zh",
            default_quiz_length=10,
            auto_tts=True,
            reverse_quiz_default=False,
            dark_mode=False,
            daily_learning_goal=10,
        )
        session.add(settings)

        folders = []
        for folder_data in sample_folders:
            folder = Folder(
                id=str(uuid.uuid4()),
                name=folder_data["name"],
                user_id=user_id,
                created_at=datetime.utcnow(),
            )
            session.add(folder)
            folders.append(folder)
        await session.flush()

        for i, data in enumerate(sample_flashcards):
            assigned_folder = folders[i % len(folders)]

            # Simulate spaced repetition metadata
            review_count = random.randint(0, 5)
            interval = random.choice([0, 1, 3, 5, 10])
            ease_factor = round(random.uniform(1.3, 2.6), 2)
            last_reviewed = date.today() - timedelta(days=interval) if review_count > 0 else None
            next_review_date = last_reviewed + timedelta(days=interval) if last_reviewed else None

            flashcard = Flashcard(
                id=str(uuid.uuid4()),
                word=data["word"],
                translation=data["translation"],
                phonetic=data["phonetic"],
                pos=data["pos"],
                example=data["example"],
                notes=data["notes"],
                source_lang=data["source_lang"],
                target_lang=data["target_lang"],
                user_id=user_id,
                folder_id=assigned_folder.id,
                created_at=datetime.utcnow(),

                # Spaced repetition fields
                review_count=review_count,
                interval=interval,
                ease_factor=ease_factor,
                last_reviewed=last_reviewed,
                next_review_date=next_review_date,
            )
            session.add(flashcard)
        await session.flush()

        for _ in range(2):
            review_session_id = str(uuid.uuid4())
            session.add(ReviewSession(
                id=review_session_id,
                user_id=user_id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 5))
            ))

            # Add 3–5 fake review events per session
            reviewed_flashcards = random.sample(sample_flashcards, k=random.randint(3, 5))
            for flash_data in reviewed_flashcards:
                matching = await session.execute(
                    text('SELECT id FROM "Flashcard" WHERE word = :word AND user_id = :user_id'),
                    {"word": flash_data["word"], "user_id": user_id}
                )
                flashcard_id = matching.scalar()
                if flashcard_id:
                    session.add(ReviewEvent(
                        id=str(uuid.uuid4()),
                        session_id=review_session_id,
                        user_id=user_id,
                        flashcard_id=flashcard_id,
                        rating=random.randint(1, 5),
                        created_at=datetime.utcnow()
                    ))

        for _ in range(2):
            quiz_session_id = str(uuid.uuid4())
            folder = random.choice(folders)

            session.add(QuizSession(
                id=quiz_session_id,
                user_id=user_id,
                folder_id=folder.id,
                include_reverse=random.choice([True, False]),
                card_count=5,
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 5))
            ))

            # Add 3–5 fake answers for the quiz
            answered_flashcards = random.sample(sample_flashcards, k=random.randint(3, 5))
            for flash_data in answered_flashcards:
                result = await session.execute(
                    text('SELECT id FROM "Flashcard" WHERE word = :word AND user_id = :user_id'),
                    {"word": flash_data["word"], "user_id": user_id}
                )
                flashcard_id = result.scalar()
                if flashcard_id:
                    session.add(QuizAnswerLog(
                        id=str(uuid.uuid4()),
                        session_id=quiz_session_id,
                        flashcard_id=flashcard_id,
                        is_correct=random.choice([True, False]),
                        answered_at=datetime.utcnow()
                    ))

        await session.commit()
        print("✅ Seeded user settings, folders, flashcards, quizzes, and review events!")

async def clear_data():
    async with AsyncSessionLocal() as session:
        await session.execute(text('DELETE FROM "Flashcard"'))
        await session.execute(text('DELETE FROM "Folder"'))
        await session.execute(text('DELETE FROM "UserSettings"'))
        await session.execute(text('DELETE FROM "QuizAnswerLog"'))
        await session.execute(text('DELETE FROM "QuizSession"'))
        await session.execute(text('DELETE FROM "ReviewEvent"'))
        await session.execute(text('DELETE FROM "ReviewSession"'))
        print("🧹 Cleared review events, sessions, flashcards, folders, quizzes, and user settings.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed or clear flashcard data.")
    parser.add_argument("action", choices=["seed", "clear"], help="Action to perform")
    args = parser.parse_args()

    asyncio.run(seed_data() if args.action == "seed" else clear_data())