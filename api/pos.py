from fastapi import FastAPI
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models import Flashcard
from database import get_db
import uuid
from fastapi.middleware.cors import CORSMiddleware
import spacy
from dotenv import load_dotenv
from openai import OpenAI
import os
from pydantic import BaseModel

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# Load English tokenizer, tagger, parser, NER
nlp = spacy.load("en_core_web_sm")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define input payload structure
class FlashcardInput(BaseModel):
    word: str
    userEmail: str

# POS endpoint (optional now)
@app.post("/pos")
def pos_tag(payload: dict):
    text = payload.get("sentence", "")
    doc = nlp(text)
    tags = [{"word": t.text, "pos": t.pos_, "dep": t.dep_} for t in doc]
    return {
        "translation": "你好世界",
        "example": "你好，世界！",
        "pos_tags": tags
    }

def generate_example_and_notes(word: str) -> tuple[str, str]:
    # mock
    return (
        f"This is a sample sentence using '{word}'.",
        f"'{word}' is used here as a placeholder noun."
    )

    # prompt = f"""You're an assistant helping language learners.
    #               Provide:
    #               1. A short, simple sentence using the word '{word}'.
    #               2. A one-sentence grammar note explaining how the word functions in the sentence.

    #               Respond in the format:
    #               Example: ...
    #               Note: ...
    #           """
    # response = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[{"role": "user", "content": prompt}],
    #     temperature=0.7,
    #     max_tokens=100
    # )

    # content = response.choices[0].message.content
    # try:
    #     example_line = next(line for line in content.splitlines() if line.lower().startswith("example:"))
    #     note_line = next(line for line in content.splitlines() if line.lower().startswith("note:"))
    #     example = example_line.split(":", 1)[1].strip()
    #     note = note_line.split(":", 1)[1].strip()
    # except Exception:
    #     example, note = "Example not found.", "Note not found."

    # return example, note

def translate_word(word: str, target_language: str = "Chinese") -> str:
    """
    Translate a word to the target language using OpenAI's API.
    """

    # mock
    return "假翻译"

    # try:
    #     system_prompt = "You are a professional translator. Provide accurate translations only."
    #     user_prompt = f"Translate the English word '{word}' to {target_language}. Return ONLY the translation characters with no explanations, notes, quotes or formatting."

    #     response = client.chat.completions.create(
    #         model="gpt-3.5-turbo",
    #         messages=[
    #             {"role": "system", "content": system_prompt},
    #             {"role": "user", "content": user_prompt}
    #         ],
    #         temperature=0.2,  # Lower temperature for more consistent output
    #         max_tokens=15,
    #     )

    #     translation = response.choices[0].message.content.strip()

    #     # Remove quotes if present
    #     translation = translation.strip('"\'')

    #     return translation

    # except Exception as e:
    #     print(f"Translation error: {str(e)}")
    #     return f"Translation unavailable"

# Flashcard endpoint
@app.post("/flashcard")
async def generate_flashcard(payload: dict, db: AsyncSession = Depends(get_db)):
    word = payload.get("word", "")
    user_id = payload.get("userId")

    if not word or not user_id:
      return {"error": "Missing word or userId"}

    doc = nlp(word)
    token = doc[0] if doc else None

    translation = translate_word(word)
    example, notes = generate_example_and_notes(word)
    phonetic = "-".join(word)

    new_flashcard = Flashcard(
        id=str(uuid.uuid4()),
        word=word,
        translation=translation,
        phonetic=phonetic,
        pos=token.pos_ if token else None,
        example=example,
        notes=notes,
        user_id=user_id
    )

    db.add(new_flashcard)
    await db.commit()
    await db.refresh(new_flashcard) # refresh to get updated fields (i.e., timestamp)

    return {
        "message": "Flashcard created",
        "data": {
            "word": word,
            "translation": translation,
            "phonetic": phonetic,
            "pos": token.pos_ if token else None,
            "example": example,
            "notes": notes
        }
    }