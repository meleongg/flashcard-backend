from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import spacy

app = FastAPI()

# Load English tokenizer, tagger, parser, NER
nlp = spacy.load("en_core_web_sm")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/pos")
def pos_tag(payload: dict):
    text = payload.get("sentence", "")
    # apply model to the text
    doc = nlp(text)
    tags = [{"word": t.text, "pos": t.pos_, "dep": t.dep_} for t in doc]
    return {
      "translation": "你好世界",
      "example": "你好，世界！",
      "pos_tags": tags
    }

@app.post("/flashcard")
def generate_flashcard(payload: dict):
    word = payload.get("word", "")
    doc = nlp(word)
    token = doc[0] if doc else None

    flashcard = {
        "word": word,
        "translation": "你好",
        "phonetic": "nǐ hǎo",
        "pos": token.pos_ if token else None,
        "example": f"{word} is commonly used in greetings.",
        "notes": "Pronoun - used to refer to the second person in Mandarin."
    }

    return flashcard