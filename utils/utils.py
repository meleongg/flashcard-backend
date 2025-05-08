import spacy

# Shared spaCy model
spacy_nlp = spacy.load("en_core_web_sm")

def get_pos(word: str):
    doc = spacy_nlp(word)
    return doc[0].pos_ if doc else None

def generate_example_and_notes(word: str):
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

def translate_word(word: str):
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