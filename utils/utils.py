import os
import re
import stanza
import spacy
from dotenv import load_dotenv
from openai import OpenAI
from langdetect import detect_langs
from api.schemas import FlashcardData
from pypinyin import pinyin, Style
from spacy.cli import download

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Cached NLP models (lazy-loaded)
_loaded_spacy = {}
_loaded_stanza = {}

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

# --- Lazy loading helpers ---
def get_spacy(lang: str):
    model_map = {
        "en": "en_core_web_sm",
        "fr": "fr_core_news_sm",
    }

    if lang not in model_map:
        return None

    if lang not in _loaded_spacy:
        model_name = model_map[lang]
        try:
            _loaded_spacy[lang] = spacy.load(model_name)
        except OSError:
            print(f"⚠️ {model_name} not found, downloading...")
            download(model_name)
            _loaded_spacy[lang] = spacy.load(model_name)
    return _loaded_spacy[lang]

def get_stanza(lang: str):
    if lang == "zh" and "zh" not in _loaded_stanza:
        _loaded_stanza["zh"] = stanza.Pipeline("zh", processors="tokenize,pos", dir="./stanza_resources", use_gpu=False)
    return _loaded_stanza.get(lang)

# --- POS tagging (language-aware) ---
def get_pos(word: str, lang: str = "en") -> str:
    if lang == "zh":
        pipeline = get_stanza("zh")
        if pipeline:
            doc = pipeline(word)
            return doc.sentences[0].words[0].upos if doc.sentences else "N/A"
    else:
        nlp = get_spacy(lang)
        if nlp:
            doc = nlp(word)
            return doc[0].pos_ if doc else "N/A"
    return "N/A"

# --- Phonetic representation ---
def get_phonetic(word: str, lang: str = "en") -> str:
    if lang == "zh":
        syllables = pinyin(word, style=Style.TONE3, errors="ignore")
        return " ".join([s[0] for s in syllables])
    return word

# --- GPT-powered flashcard creation ---
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
        "You are a helpful assistant for language learners.\n"
        "Given a vocabulary word, provide:\n"
        "1. An accurate translation\n"
        "2. A simple sentence using the word\n"
        "3. A grammar note explaining its usage\n\n"
        "Format your response as:\n"
        "Translation: ...\nExample: ...\nNote: ..."
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
            max_tokens=150
        )
        content = response.choices[0].message.content

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
        print(f"[GPT Error] {str(e)}")
        return "Translation unavailable", "Example not found.", "Note not found."