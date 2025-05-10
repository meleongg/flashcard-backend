import spacy
from api.schemas import FlashcardData

async def generate_flashcard_data(word: str, source_lang: str, target_lang: str) -> FlashcardData:
    translation = translate_word(word, source_lang, target_lang)
    example, notes = generate_example_and_notes(word, source_lang, target_lang)
    phonetic = "-".join(word)
    pos = get_pos(word, lang=source_lang)

    return FlashcardData(
        word=word,
        translation=translation,
        phonetic=phonetic,
        pos=pos,
        example=example,
        notes=notes,
    )

# Shared spaCy model
spacy_nlp = spacy.load("en_core_web_sm")

def get_pos(word: str, lang: str = "en"):
    if lang != "en":
        return "N/A"
    doc = spacy_nlp(word)
    return doc[0].pos_ if doc else None

def generate_example_and_notes(word: str, source_lang: str = "en", target_lang: str = "zh"):
    return (
        f"This is a sample {source_lang} sentence using '{word}'.",
        f"'{word}' is used here as a placeholder from {source_lang} to {target_lang}."
    )

    # prompt = f"""You're an assistant helping language learners.
    # Provide:
    # 1. A short, simple sentence using the word '{word}' in {source_lang}.
    # 2. A one-sentence grammar note explaining how the word functions in the sentence.

    # Format your response exactly as:
    # Example: ...
    # Note: ...
    # """

    # try:
    #     response = client.chat.completions.create(
    #         model="gpt-3.5-turbo",
    #         messages=[{"role": "user", "content": prompt}],
    #         temperature=0.7,
    #         max_tokens=100
    #     )

    #     content = response.choices[0].message.content
    #     example_line = next(line for line in content.splitlines() if line.lower().startswith("example:"))
    #     note_line = next(line for line in content.splitlines() if line.lower().startswith("note:"))

    #     example = example_line.split(":", 1)[1].strip()
    #     note = note_line.split(":", 1)[1].strip()

    #     return example, note

    # except Exception:
    #     return "Example not found.", "Note not found."

def translate_word(word: str, source_lang: str = "en", target_lang: str = "zh") -> str:
    return "假翻译"  # fallback mock

    # try:
    #     system_prompt = "You are a professional translator. Provide accurate translations only."
    #     user_prompt = (
    #         f"Translate the word '{word}' from {source_lang} to {target_lang}. "
    #         f"Return ONLY the translation with no quotes, notes, or formatting."
    #     )

    #     response = client.chat.completions.create(
    #         model="gpt-3.5-turbo",
    #         messages=[
    #             {"role": "system", "content": system_prompt},
    #             {"role": "user", "content": user_prompt}
    #         ],
    #         temperature=0.2,
    #         max_tokens=15,
    #     )

    #     translation = response.choices[0].message.content.strip()
    #     return translation.strip('"\'')

    # except Exception as e:
    #     print(f"Translation error: {str(e)}")
    #     return "Translation unavailable"