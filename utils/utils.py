import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from langdetect import detect_langs
from api.schemas import FlashcardData
from pypinyin import pinyin, Style

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

# --- Phonetic representation ---
def get_phonetic(word: str, lang: str = "en") -> str:
    if lang == "zh":
        syllables = pinyin(word, style=Style.TONE3, errors="ignore")
        return " ".join([s[0] for s in syllables])
    return word

# --- GPT-powered flashcard creation ---
async def generate_flashcard_data(word: str, source_lang: str, target_lang: str) -> FlashcardData:
    translation, example, notes, pos = generate_flashcard_with_gpt(word, source_lang, target_lang)
    phonetic = get_phonetic(word, lang=source_lang)

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
        "You are a helpful assistant for language learners.\n"
        "Given a vocabulary word, provide:\n"
        "1. An accurate translation\n"
        "2. A simple sentence using the word\n"
        "3. A grammar note explaining its usage\n"
        "4. The word's part of speech (Noun, Verb, Adjective, etc.)\n\n"
        "Format your response as:\n"
        "Translation: ...\nExample: ...\nNote: ...\nPOS: ..."
    )
    user_prompt = f"Word: '{word}'\nSource Language: {source_lang}\nTarget Language: {target_lang}"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
            max_tokens=200
        )

        content = response.choices[0].message.content

        translation, example, note, pos = "", "", "", ""
        for line in content.splitlines():
            if line.lower().startswith("translation:"):
                translation = line.split(":", 1)[1].strip()
            elif line.lower().startswith("example:"):
                example = line.split(":", 1)[1].strip()
            elif line.lower().startswith("note:"):
                note = line.split(":", 1)[1].strip()
            elif line.lower().startswith("pos:"):
                pos = line.split(":", 1)[1].strip()

        return translation or "Translation unavailable", example, note, pos

    except Exception as e:
        print(f"[GPT Error] {str(e)}")
        return "Translation unavailable", "Example not found.", "Note not found.", "N/A"