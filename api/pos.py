from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import spacy
from dotenv import load_dotenv
from openai import OpenAI
import os

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
    prompt = f"""You're an assistant helping language learners.
                  Provide:
                  1. A short, simple sentence using the word '{word}'.
                  2. A one-sentence grammar note explaining how the word functions in the sentence.

                  Respond in the format:
                  Example: ...
                  Note: ...
              """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=100
    )

    content = response.choices[0].message.content
    try:
        example_line = next(line for line in content.splitlines() if line.lower().startswith("example:"))
        note_line = next(line for line in content.splitlines() if line.lower().startswith("note:"))
        example = example_line.split(":", 1)[1].strip()
        note = note_line.split(":", 1)[1].strip()
    except Exception:
        example, note = "Example not found.", "Note not found."

    return example, note

def translate_word(word: str, target_language: str = "Chinese") -> str:
    prompt = f"Translate the word '{word}' to {target_language}. Respond with the translation only."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=20,
    )

    return response.choices[0].message.content.strip()

# Flashcard endpoint
@app.post("/flashcard")
def generate_flashcard(payload: dict):
    word = payload.get("word", "")
    doc = nlp(word)
    token = doc[0] if doc else None

    # 🔹 NEW: dynamic translation
    translation = translate_word(word)

    # Still mocked, update later
    phonetic = "-".join(word)

    example, notes = generate_example_and_notes(word)

    return {
        "word": word,
        "translation": translation,
        "phonetic": phonetic,
        "pos": token.pos_ if token else None,
        "example": example,
        "notes": notes
    }