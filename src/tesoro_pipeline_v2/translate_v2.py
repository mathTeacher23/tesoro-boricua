#!/usr/bin/env python3
"""
Translate V2: Translate consolidated definitions from Spanish to English

Input: ../../data/preprocessed/preprocessed_tesoro_v2/ (from preprocess_v2.py)
Output: ../../data/translated/translated_tesoro_v2/ (with English translations)
"""

import os
import json
from pathlib import Path
from tqdm import tqdm
from typing import List
from transformers import pipeline

# Load translation pipeline (Helsinki-NLP/opus-mt-es-en: accurate and free)
print("Loading translation model...")
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-es-en")

# Input/output directories (reference TESORO_BORICUA level - 3 directories up)
TESORO_ROOT = Path(__file__).parent.parent.parent
INPUT_DIR = TESORO_ROOT / "data" / "preprocessed" / "preprocessed_tesoro_v2"
OUTPUT_DIR = TESORO_ROOT / "data" / "translated" / "translated_tesoro_v2"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def translate_definitions(es_defs: List[str]) -> List[str]:
    """
    Translate a list of Spanish definitions to English.

    Args:
        es_defs: List of Spanish definition strings

    Returns:
        List of English translations
    """
    en_defs = []
    for defn in es_defs:
        if not defn or not defn.strip():
            en_defs.append("")
            continue

        try:
            result = translator(defn, max_length=1000)[0]['translation_text']
            en_defs.append(result)
        except Exception as e:
            print(f"    ⚠️ Failed to translate: {defn[:50]}... → {e}")
            en_defs.append("")  # Keep index consistency
    return en_defs


def process_file(file_path: Path):
    """Process a single preprocessed file and translate definitions."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"  Translating {len(data)} entries from {file_path.name}...")

    updated_data = []
    for entry in tqdm(data, desc=f"  {file_path.name}", leave=False):
        if entry.get("en_definitions") and entry["en_definitions"][0]:
            # Already translated
            updated_data.append(entry)
            continue

        es_defs = entry.get("es_definitions", [])
        en_defs = translate_definitions(es_defs)
        entry["en_definitions"] = en_defs
        updated_data.append(entry)

    # Save translated version
    # Change "transformed" to "translated" in the filename
    new_name = file_path.name.replace("transformed_", "translated_")
    out_path = OUTPUT_DIR / new_name

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)

    print(f"  ✅ Saved: {out_path}")


def translate_all_files():
    """Translate all preprocessed files."""
    if not INPUT_DIR.exists():
        print(f"❌ Input directory not found: {INPUT_DIR}")
        return

    json_files = sorted(INPUT_DIR.glob("transformed_*.json"))

    if not json_files:
        print(f"⚠️  No files found in {INPUT_DIR}")
        return

    print(f"Found {len(json_files)} files to translate")

    for file_path in json_files:
        process_file(file_path)

    print(f"\n✅ Translation complete. Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESORO V2 TRANSLATION: Spanish → English")
    print("="*80 + "\n")
    translate_all_files()
