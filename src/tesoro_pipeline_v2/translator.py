#!/usr/bin/env python3
"""
TESORO Translation Pipeline (2025)

Translates consolidated Spanish definitions to English.

Input:  data/preprocessed/preprocessed_tesoro_v2/<letter>/<word>.json
Output: data/translated/translated_tesoro_v2/<letter>/<word>.json

Maintains the exact same JSON structure, adding English translations to:
  - en_definitions array (list of all translated superscript definitions)
  - Each superscript gets an "en_consolidated_definition" field

Usage:
    python translate.py

Dependencies:
    pip install translate tqdm
"""

import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm

try:
    from translate import Translator
except ImportError:
    print("❌ Error: translate library not installed")
    print("   Install with: pip install translate")
    sys.exit(1)

# Paths
TESORO_ROOT = Path(__file__).parent.parent.parent
INPUT_DIR = TESORO_ROOT / "data" / "preprocessed" / "preprocessed_tesoro_v2"
OUTPUT_DIR = TESORO_ROOT / "data" / "translated" / "translated_tesoro_v2"

# Initialize translator
print("Initializing Spanish → English translator...")
translator = Translator(from_lang="es", to_lang="en")
print("✅ Translator ready\n")


def translate_text(text: str) -> str:
    """
    Translate a single Spanish text to English.

    Args:
        text: Spanish text to translate

    Returns:
        English translation
    """
    if not text or not text.strip():
        return ""

    try:
        # Use the translate library (uses MyMemory API)
        result = translator.translate(text)

        # Small delay to avoid rate limiting
        time.sleep(0.1)

        return result

    except Exception as e:
        print(f"    ⚠️ Translation failed: {str(e)[:100]}")
        # Try again after a short delay
        try:
            time.sleep(1)
            result = translator.translate(text)
            return result
        except:
            return ""


def translate_word_file(input_file: Path, output_file: Path) -> bool:
    """
    Translate a single word file from Spanish to English.

    Args:
        input_file: Path to preprocessed JSON file
        output_file: Path to save translated JSON file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Load preprocessed data
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check if already translated
        if data.get("en_definitions") and len(data["en_definitions"]) > 0:
            if all(d.strip() for d in data["en_definitions"]):
                # Already fully translated, skip
                return True

        # Translate each superscript's consolidated definition
        en_definitions = []

        for superscript, sup_data in data.get("superscripts", {}).items():
            es_def = sup_data.get("consolidated_definition", "")

            # Translate
            en_def = translate_text(es_def)

            # Add English definition to superscript data
            sup_data["en_consolidated_definition"] = en_def

            # Add to main en_definitions array
            en_definitions.append(en_def)

        # Update main en_definitions array
        data["en_definitions"] = en_definitions

        # Save translated file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return True

    except Exception as e:
        print(f"    ❌ Error processing {input_file.name}: {e}")
        return False


def translate_all_letters():
    """Process all letters and translate all words."""
    print("="*80)
    print("TESORO TRANSLATION PIPELINE: Spanish → English")
    print("="*80)

    if not INPUT_DIR.exists():
        print(f"❌ Input directory not found: {INPUT_DIR}")
        return False

    alphabet = list("abcdefghijklmnopqrstuvwxyz") + ["ñ"]
    total_processed = 0
    total_failed = 0

    for letter in alphabet:
        input_letter_dir = INPUT_DIR / letter.lower()

        if not input_letter_dir.exists():
            continue

        json_files = sorted(input_letter_dir.glob("*.json"))

        if not json_files:
            continue

        print(f"\n{'='*80}")
        print(f"TRANSLATING LETTER '{letter.upper()}' - {len(json_files)} words")
        print(f"{'='*80}\n")

        processed = 0
        failed = 0

        # Use tqdm for progress bar
        for json_file in tqdm(json_files, desc=f"  Letter {letter.upper()}", unit="word"):
            word = json_file.stem
            output_file = OUTPUT_DIR / letter.lower() / f"{word}.json"

            if translate_word_file(json_file, output_file):
                processed += 1
            else:
                failed += 1

        total_processed += processed
        total_failed += failed

        print(f"\n  ✅ Letter '{letter.upper()}' complete: {processed} words translated, {failed} failed")

    print(f"\n{'='*80}")
    print(f"TRANSLATION COMPLETE")
    print(f"{'='*80}")
    print(f"  Total words translated: {total_processed}")
    print(f"  Failed: {total_failed}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print()

    return True


if __name__ == "__main__":
    success = translate_all_letters()
    sys.exit(0 if success else 1)
