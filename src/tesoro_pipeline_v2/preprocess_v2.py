#!/usr/bin/env python3
"""
Preprocess V2: Consolidate raw definitions and transform into uniform format

Pipeline:
1. CONSOLIDATION: Consolidate raw definitions with fallback strategy
   - Input: ../../webscrape/data/raw_tesoro_v2/ (raw definition JSON files)
   - Output: ../../webscrape/data/preprocessed_tesoro_v2/ (consolidated JSON files)

2. PREPROCESSING: Transform consolidated definitions into uniform format
   - Input: ../../webscrape/data/preprocessed_tesoro_v2/ (consolidated definitions)
   - Output: ../../data/preprocessed/preprocessed_tesoro_v2/ (transformed for react_ui)

Usage:
    python preprocess_v2.py              # Run both consolidation and preprocessing
    python preprocess_v2.py --consolidate-only  # Run only consolidation
    python preprocess_v2.py --preprocess-only   # Run only preprocessing (assumes consolidation done)
"""

import os
import json
import sys
import subprocess
from pathlib import Path
from collections import Counter
from consolidate import DefinitionConsolidatorFinal

# Paths (reference TESORO_BORICUA level - 3 directories up from tesoro_pipeline_v2)
TESORO_ROOT = Path(__file__).parent.parent.parent
RAW_DATA_DIR = TESORO_ROOT / "data" / "raw" / "raw_tesoro_v2"
CONSOLIDATED_DATA_DIR = TESORO_ROOT / "data" / "consolidated" / "consolidated_tesoro_v2"
OUTPUT_DIR = TESORO_ROOT / "data" / "preprocessed" / "preprocessed_tesoro_v2"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# STAGE 1: CONSOLIDATION
# ============================================================================

def consolidate_letter(letter: str, verbose: bool = True) -> bool:
    """Consolidate all words for a single letter."""

    raw_path = RAW_DATA_DIR / letter
    preprocessed_path = CONSOLIDATED_DATA_DIR / letter

    if not raw_path.exists():
        print(f"❌ Raw data folder not found: {raw_path}")
        return False

    # Create preprocessed folder if it doesn't exist
    preprocessed_path.mkdir(parents=True, exist_ok=True)

    # Get all JSON files in raw folder
    json_files = sorted(raw_path.glob("*.json"))

    if not json_files:
        print(f"⚠️  No JSON files found in {raw_path}")
        return False

    print(f"\n{'='*80}")
    print(f"CONSOLIDATING LETTER '{letter.upper()}' - {len(json_files)} words")
    print(f"{'='*80}\n")

    processed = 0
    failed = 0

    for idx, json_file in enumerate(json_files, 1):
        try:
            word = json_file.stem
            print(f"  [{idx:>4}/{len(json_files)}] {word}...", end=" ")

            # Load and consolidate
            consolidator = DefinitionConsolidatorFinal(str(json_file))
            analysis = consolidator.analyze_by_superscript()

            # Generate consolidated definitions for each variant
            consolidated_output = {}
            for superscript, sup_data in analysis.items():
                all_defs = [d['text'] for d in sup_data['all_definitions']]

                # Generate single consolidated definition per variant
                consolidated_def, analysis_meta, could_not_consolidate = consolidator.generate_consolidated_definition(all_defs)

                # Assess stability
                stability, similarity_score = consolidator.assess_definition_stability(all_defs)

                # Consolidate themes
                all_themes = []

                # Load raw data to get actual themes array
                raw_file = Path(str(json_file))
                with open(raw_file, 'r', encoding='utf-8') as rf:
                    raw_data = json.load(rf)

                # Extract themes from raw data by variant/superscript
                for entry in raw_data[consolidator.word]:
                    if entry['superscript'] == superscript:
                        for def_item in entry['details']['definition_list']:
                            for sub_item in def_item['definition_sublist']:
                                if sub_item.get('themes'):
                                    all_themes.extend(sub_item['themes'])

                # Count themes and get top 3
                theme_counts = Counter(all_themes)
                consolidated_themes = [theme for theme, count in theme_counts.most_common(3)]
                # all_themes_found contains all unique themes found across all definitions
                all_themes_found = sorted(list(set(all_themes)))

                consolidated_output[superscript] = {
                    'consolidated_definition': consolidated_def,
                    'could_not_consolidate': could_not_consolidate,
                    'num_definitions_analyzed': len(all_defs),
                    'definition_stability': stability,
                    'semantic_similarity_score': similarity_score,
                    'consolidated_themes': consolidated_themes,
                    'all_themes_found': all_themes_found,
                    'years': sup_data['years'],
                    'sources': sup_data['sources'],
                    'origin': sup_data['origin'],
                    'grammar': sup_data['grammar'],
                    'related_words': sup_data['related_words'],
                    'analysis_method': analysis_meta.get('method', 'Extractive base with semantic validation'),
                    'reference_definitions': [d['text'][:150] + '...' if len(d['text']) > 150 else d['text']
                                             for d in sup_data['all_definitions'][:3]]
                }

            # Save consolidated version
            output_file = preprocessed_path / f"{word}_consolidated.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({word: consolidated_output}, f, indent=2, ensure_ascii=False)

            print("✅")
            processed += 1

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            failed += 1

    # Summary
    print(f"\n{'='*80}")
    print(f"CONSOLIDATION COMPLETE")
    print(f"{'='*80}")
    print(f"  Letter:        {letter.upper()}")
    print(f"  Processed:     {processed}")
    print(f"  Failed:        {failed}")
    print(f"  Output folder: {preprocessed_path}")
    print()

    return processed > 0


def run_consolidation():
    """Run consolidation for all letters."""
    print("\n" + "="*80)
    print("STAGE 1: CONSOLIDATION - Raw Definitions → Consolidated Definitions")
    print("="*80)

    if not RAW_DATA_DIR.exists():
        print(f"❌ Raw data directory not found: {RAW_DATA_DIR}")
        return False

    alphabet = list("abcdefghijklmnopqrstuvwxyz") + ["ñ"]

    completed = 0
    failed = 0

    for letter in alphabet:
        if consolidate_letter(letter):
            completed += 1
        else:
            failed += 1

    print(f"\n{'='*80}")
    print(f"CONSOLIDATION SUMMARY")
    print(f"{'='*80}")
    print(f"Completed: {completed}/27")
    print(f"Failed:    {failed}/27")
    print()

    return failed == 0


# ============================================================================
# STAGE 2: PREPROCESSING
# ============================================================================

def process_consolidated_letter(letter: str):
    """
    Process all consolidated words for a single letter.
    Creates individual .json files per word, matching raw directory structure.

    Args:
        letter: Single letter (a-z, ñ)
    """
    letter_dir = CONSOLIDATED_DATA_DIR / letter.lower()
    output_letter_dir = OUTPUT_DIR / letter.lower()

    if not letter_dir.exists():
        print(f"❌ Letter directory not found: {letter_dir}")
        return False

    # Create output directory for this letter
    output_letter_dir.mkdir(parents=True, exist_ok=True)

    json_files = sorted(letter_dir.glob("*_consolidated.json"))

    if not json_files:
        print(f"⚠️  No consolidated files found for letter {letter.upper()}")
        return False

    print(f"\n📄 Processing letter {letter.upper()} ({len(json_files)} words)...")

    processed = 0
    failed = 0

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Data structure: {"word": {"superscript": {...}, ...}}
            for word, superscripts in data.items():
                # Fix underscores to spaces in term names
                term = word.replace("_", " ")

                # Create one entry per word (consolidate all superscripts into one entry)
                entry = {
                    "letter": letter.upper(),
                    "term": term,
                    "superscripts": {},  # Will hold superscript data
                    "es_definitions": [],
                    "en_definitions": [],  # Will be filled by translate_v2.py
                    "source": "https://tesoro.pr",
                }

                # Process all superscripts for this word
                for superscript, con_data in superscripts.items():
                    entry["superscripts"][superscript] = {
                        "consolidated_definition": con_data.get("consolidated_definition", ""),
                        "could_not_consolidate": con_data.get("could_not_consolidate", False),
                        "consolidation_metadata": {
                            "num_definitions_analyzed": con_data.get("num_definitions_analyzed"),
                            "definition_stability": con_data.get("definition_stability"),
                            "semantic_similarity_score": con_data.get("semantic_similarity_score"),
                            "grammar": con_data.get("grammar", []),
                            "themes": con_data.get("consolidated_themes", []),
                            "all_themes_found": con_data.get("all_themes_found", []),
                            "sources": con_data.get("sources", []),
                            "years": con_data.get("years", []),
                            "origin": con_data.get("origin"),
                            "related_words": con_data.get("related_words", []),
                            "reference_definitions": con_data.get("reference_definitions", [])
                        }
                    }
                    # Add first consolidated definition to es_definitions
                    entry["es_definitions"].append(con_data.get("consolidated_definition", ""))

                # Save individual word file matching raw structure
                # Use underscore format to match raw file naming
                output_file = output_letter_dir / f"{word}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(entry, f, ensure_ascii=False, indent=2)

                processed += 1

        except Exception as e:
            print(f"  ❌ Error processing {json_file.name}: {e}")
            failed += 1
            continue

    if processed == 0:
        print(f"  ⚠️  No words processed for letter {letter.upper()}")
        return False

    print(f"  ✅ Created {processed} individual word files in {output_letter_dir.name}/")
    if failed > 0:
        print(f"  ⚠️  {failed} files failed to process")
    return True


def run_preprocessing():
    """Run preprocessing for all letters."""
    print("\n" + "="*80)
    print("STAGE 2: PREPROCESSING - Consolidated → Individual Word Files")
    print("="*80)
    print("\nCreating individual .json files per word (matching raw directory structure)")

    # Get all letter directories
    if not CONSOLIDATED_DATA_DIR.exists():
        print(f"\n❌ Consolidated data directory not found: {CONSOLIDATED_DATA_DIR}")
        print("Make sure consolidation has been run first.")
        return False

    letter_dirs = sorted([d.name for d in CONSOLIDATED_DATA_DIR.iterdir() if d.is_dir()])

    if not letter_dirs:
        print(f"❌ No letter directories found in {CONSOLIDATED_DATA_DIR}")
        return False

    print(f"Found {len(letter_dirs)} letter directories: {', '.join([l.upper() for l in letter_dirs])}")

    successful = 0
    failed = 0

    for letter in letter_dirs:
        if process_consolidated_letter(letter):
            successful += 1
        else:
            failed += 1

    # Final summary
    print(f"\n{'='*80}")
    print(f"PREPROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"  Successful letters: {successful}")
    print(f"  Failed letters:     {failed}")
    print(f"  Output structure:   {OUTPUT_DIR}/")
    print(f"                      ├── a/")
    print(f"                      │   ├── word1.json")
    print(f"                      │   ├── word2.json")
    print(f"                      │   └── ...")
    print(f"                      ├── b/")
    print(f"                      └── ...")
    print()

    return failed == 0


def main():
    """Main entry point."""

    if len(sys.argv) > 1:
        flag = sys.argv[1].lower()

        if flag == "--consolidate-only":
            return run_consolidation()
        elif flag == "--preprocess-only":
            return run_preprocessing()
        else:
            print(f"Unknown flag: {flag}")
            print("Usage:")
            print("  python preprocess_v2.py              # Run both consolidation and preprocessing")
            print("  python preprocess_v2.py --consolidate-only  # Run only consolidation")
            print("  python preprocess_v2.py --preprocess-only   # Run only preprocessing")
            sys.exit(1)

    # Default: run both consolidation and preprocessing
    print("\n" + "="*80)
    print("TESORO V2 PIPELINE: Consolidation + Preprocessing")
    print("="*80)

    consolidation_success = run_consolidation()

    if consolidation_success:
        preprocessing_success = run_preprocessing()
        return preprocessing_success
    else:
        print("❌ Consolidation failed, skipping preprocessing")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
