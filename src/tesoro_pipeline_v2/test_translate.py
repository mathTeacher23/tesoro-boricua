#!/usr/bin/env python3
"""
Test script for translator.py

Tests translation on a single word (piragua) to verify the pipeline works.
"""

import json
from pathlib import Path
from translator import translate_text, translate_word_file

TESORO_ROOT = Path(__file__).parent.parent.parent
INPUT_FILE = TESORO_ROOT / "data" / "preprocessed" / "preprocessed_tesoro_v2" / "p" / "piragua.json"
OUTPUT_FILE = TESORO_ROOT / "data" / "translated" / "translated_tesoro_v2" / "p" / "piragua.json"

print("\n" + "="*80)
print("TRANSLATION TEST: piragua.json")
print("="*80)

print(f"\nInput file: {INPUT_FILE}")
print(f"Output file: {OUTPUT_FILE}")

if not INPUT_FILE.exists():
    print(f"❌ Input file not found: {INPUT_FILE}")
    exit(1)

# Load input file
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"\nWord: {data['term']}")
print(f"Superscripts: {list(data['superscripts'].keys())}")

print("\n" + "-"*80)
print("SPANISH DEFINITIONS:")
print("-"*80)

for superscript, sup_data in data['superscripts'].items():
    es_def = sup_data.get('consolidated_definition', '')
    print(f"\nSuperscript {superscript}:")
    print(f"  ES: {es_def}")

# Translate the file
print("\n" + "-"*80)
print("TRANSLATING...")
print("-"*80)

success = translate_word_file(INPUT_FILE, OUTPUT_FILE)

if success:
    print("✅ Translation successful")

    # Load and display translated file
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        translated = json.load(f)

    print("\n" + "-"*80)
    print("ENGLISH TRANSLATIONS:")
    print("-"*80)

    for superscript, sup_data in translated['superscripts'].items():
        en_def = sup_data.get('en_consolidated_definition', '')
        print(f"\nSuperscript {superscript}:")
        print(f"  EN: {en_def}")

    print("\n" + "-"*80)
    print("EN_DEFINITIONS ARRAY:")
    print("-"*80)
    for i, en_def in enumerate(translated.get('en_definitions', []), 1):
        print(f"{i}. {en_def}")

    print("\n" + "="*80)
    print("✅ TEST PASSED")
    print("="*80)
else:
    print("❌ Translation failed")
    exit(1)
