import os
import json
from pathlib import Path
from tqdm import tqdm
from typing import List
from transformers import pipeline

# Load translation pipeline (this uses a local model from HuggingFace — accurate and free)
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-es-en")

# Input/output directories
INPUT_DIR = Path("data/preprocessed/preprocessed_dialecto")
OUTPUT_DIR = Path("data/translated/translated_dialecto")
OUTPUT_DIR.mkdir(exist_ok=True)

def translate_definitions(es_defs: List[str]) -> List[str]:
    """
    Translate a list of Spanish definitions to English.
    """
    en_defs = []
    for defn in es_defs:
        try:
            result = translator(defn, max_length=1000)[0]['translation_text']
            en_defs.append(result)
        except Exception as e:
            print(f"⚠️ Failed to translate: {defn} → {e}")
            en_defs.append("")  # Keep index consistency
    return en_defs

def process_file(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated_data = []
    for entry in tqdm(data, desc=f"Translating {file_path.name}"):
        if entry.get("en_definitions"):
            # Already translated
            updated_data.append(entry)
            continue

        es_defs = entry.get("es_definitions", [])
        en_defs = translate_definitions(es_defs)
        entry["en_definitions"] = en_defs
        updated_data.append(entry)

    # Save translated version
    # Change "transformed_tesoro" to "translated_tesoro" in the filename
    new_name = file_path.name.replace("transformed_tesoro", "translated_tesoro")
    out_path = OUTPUT_DIR / new_name

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved: {out_path}")

def translate_all_files():
    json_files = list(INPUT_DIR.glob("*.json"))
    for file_path in json_files:
        process_file(file_path)

if __name__ == "__main__":
    translate_all_files()