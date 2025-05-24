import os
import re
import spacy
import stanza
from langdetect import detect_langs
from openai import OpenAI
from dotenv import load_dotenv
from api.schemas import FlashcardData
from pypinyin import pinyin, Style

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- NLP model setup ---
# Load spaCy models
spacy_models = {
    "en": spacy.load("en_core_web_sm"),
    "fr": spacy.load("fr_core_news_sm")
}

spacy_nlp = spacy.load("en_core_web_sm")
stanza.download("zh")  # Ensure downloaded before loading
stanza_zh = stanza.Pipeline("zh", processors="tokenize,pos", use_gpu=False)

def get_phonetic(word: str, lang: str = "en") -> str:
    if lang == "zh":
        # Returns pinyin with tone marks
        syllables = pinyin(word, style=Style.TONE3, errors='ignore')
        return " ".join([s[0] for s in syllables])
    else:
        return word

# --- Language detection ---
def detect_language(text: str, threshold: float = 0.8) -> str:
    try:
        langs = detect_langs(text)
        if langs:
            top_lang = langs[0]
            if top_lang.prob >= threshold:
                return top_lang.lang
    except Exception:
        pass
    if re.search(r'[\u4e00-\u9fff]', text):
        return "zh"
    return "unknown"

# --- POS tagging (language-aware) ---
def get_pos(word: str, lang: str = "en") -> str:
    if lang == "zh":
        doc = stanza_zh(word)
        return doc.sentences[0].words[0].upos if doc.sentences else "N/A"
    elif lang in spacy_models:
        doc = spacy_models[lang](word)
        return doc[0].pos_ if doc else "N/A"
    return "N/A"

# --- Flashcard generation ---
async def generate_flashcard_data(word: str, source_lang: str, target_lang: str) -> FlashcardData:
    translation, example, notes = generate_flashcard_with_gpt(word, source_lang, target_lang)
    phonetic = get_phonetic(word, lang=source_lang)
    pos = get_pos(word, lang=source_lang)

    return FlashcardData(
        word=word,
        translation=translation,
        phonetic=phonetic,
        pos=pos,
        example=example,
        notes=notes,
    )

def generate_flashcard_with_gpt(word: str, source_lang: str, target_lang: str):
    system_prompt = (
        "You are a helpful assistant for language learners. "
        "Given a vocabulary word, provide: \n"
        "1. An accurate translation from the source language to the target language.\n"
        "2. A simple example sentence using the word in the source language.\n"
        "3. A short grammar note explaining how the word is used in the sentence.\n\n"
        "Format your response **exactly** as:\n"
        "Translation: ...\n"
        "Example: ...\n"
        "Note: ..."
    )

    user_prompt = (
        f"Word: '{word}'\n"
        f"Source Language: {source_lang}\n"
        f"Target Language: {target_lang}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
            max_tokens=150
        )

        content = response.choices[0].message.content

        # Parse output (robustly in case of slight formatting issues)
        translation, example, note = "", "", ""
        for line in content.splitlines():
            if line.lower().startswith("translation:"):
                translation = line.split(":", 1)[1].strip()
            elif line.lower().startswith("example:"):
                example = line.split(":", 1)[1].strip()
            elif line.lower().startswith("note:"):
                note = line.split(":", 1)[1].strip()

        return translation or "Translation unavailable", example, note

    except Exception as e:
        print(f"[GPT Generation Error] {str(e)}")
        return "Translation unavailable", "Example not found.", "Note not found."