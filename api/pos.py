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