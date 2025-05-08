import json
import os
import pickle
from sentence_transformers import SentenceTransformer

def load_cedict_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def embed_definitions(cedict_data, model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    entries = []

    for simplified, defs in cedict_data.items():
        for entry in defs:
            definition_text = " / ".join(entry["definitions"])
            embedding = model.encode(definition_text)
            entries.append({
                "simplified": simplified,
                "traditional": entry["traditional"],
                "pinyin": entry["pinyin"],
                "definition": definition_text,
                "embedding": embedding
            })

    return entries

def save_embeddings(entries, path):
    with open(path, "wb") as f:
        pickle.dump(entries, f)

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    json_path = os.path.join(base_dir, "../data/cedict.json")
    output_path = os.path.join(base_dir, "../data/cedict_embeddings.pkl")

    cedict = load_cedict_json(json_path)
    embedded = embed_definitions(cedict)
    save_embeddings(embedded, output_path)
    print(f"Saved {len(embedded)} embedded entries to {output_path}")