import gzip
import os
import json
from collections import defaultdict

def parse_cedict_line(line):
    # Skip comments and empty lines
    if line.startswith("#") or not line.strip():
        return None

    try:
        # Example format: 傳統詞語 简化词语 [pinyin] /definition1/definition2/
        trad, rest = line.strip().split(" ", 1)
        simp, rest = rest.split(" ", 1)
        pinyin = rest[rest.find("[")+1 : rest.find("]")]
        definitions = rest[rest.find("/") + 1 :].strip("/").split("/")
        return {
            "traditional": trad,
            "simplified": simp,
            "pinyin": pinyin,
            "definitions": definitions
        }
    except Exception:
        return None

def parse_cedict_to_dict(file_path):
    cedict = defaultdict(list)

    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
        for line in f:
            parsed = parse_cedict_line(line)
            if parsed:
                key = parsed["simplified"]
                cedict[key].append(parsed)

    return cedict

def preview_entries(cedict_dict, n=5):
    for i, (simp, entries) in enumerate(cedict_dict.items()):
        print(f"{simp}: {entries}")
        if i + 1 >= n:
            break

def export_to_json(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Exported to {output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    cedict_path = os.path.join(base_dir, "../data/cedict_1_0_ts_utf-8_mdbg.txt.gz")
    output_path = os.path.join(base_dir, "../data/cedict.json")

    cedict_data = parse_cedict_to_dict(cedict_path)
    preview_entries(cedict_data)
    export_to_json(cedict_data, output_path)