#!/usr/bin/env python3
"""
Unit test for preprocess.py

Tests the unified pipeline on a single sample file from raw data.
"""

import json
import sys
from pathlib import Path

# Import the components from preprocess.py
from preprocess import (
    DefinitionConsolidator,
    write_preprocessed_word,
    TESORO_ROOT,
    OUTPUT_DIR
)

def test_single_file():
    """Test consolidation and preprocessing on a single sample file."""

    # Use a small test file
    test_file = TESORO_ROOT / "data" / "raw" / "raw_tesoro_v2" / "p" / "piragua.json"

    print("\n" + "="*80)
    print("UNIT TEST: Single File Processing")
    print("="*80)
    print(f"\nTesting file: {test_file}")

    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False

    try:
        print("\n[1/3] Loading raw data...")
        with open(test_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        word_key = list(raw_data.keys())[0]
        print(f"✅ Loaded word: '{word_key}'")
        print(f"   Entries: {len(raw_data[word_key])}")

        print("\n[2/3] Running consolidation...")
        consolidator = DefinitionConsolidator(str(test_file))
        consolidated_report = consolidator.run()

        print("✅ Consolidation complete")
        for word, superscripts in consolidated_report.items():
            print(f"   Word: {word}")
            for sup, result in superscripts.items():
                consolidated_def = result.get('hybrid_summary', '') or result.get('consolidated', '')
                print(f"     Superscript {sup}:")
                print(f"       Definitions analyzed: {result.get('raw_definition_count', 0)}")
                print(f"       Stability: {result.get('stability', 0.0)}")
                print(f"       Consolidated: {consolidated_def[:80]}...")

        print("\n[3/3] Writing preprocessed output...")
        word = test_file.stem
        letter = test_file.parent.name

        write_preprocessed_word(letter, word, raw_data, consolidated_report)

        # Verify output file was created
        output_file = OUTPUT_DIR / letter / f"{word}.json"
        if output_file.exists():
            print(f"✅ Output file created: {output_file}")

            # Display the output
            with open(output_file, 'r', encoding='utf-8') as f:
                output_data = json.load(f)

            print(f"\nOutput structure:")
            print(f"  Letter: {output_data['letter']}")
            print(f"  Term: {output_data['term']}")
            print(f"  Superscripts: {list(output_data['superscripts'].keys())}")
            print(f"  ES Definitions: {len(output_data['es_definitions'])}")

            # Show first superscript details
            first_sup = list(output_data['superscripts'].keys())[0]
            sup_data = output_data['superscripts'][first_sup]
            print(f"\n  Superscript '{first_sup}' details:")
            print(f"    Consolidated definition: {sup_data['consolidated_definition'][:60]}...")
            print(f"    Could not consolidate: {sup_data['could_not_consolidate']}")
            print(f"    Metadata keys: {list(sup_data['consolidation_metadata'].keys())}")

            print("\n" + "="*80)
            print("✅ TEST PASSED")
            print("="*80)
            return True
        else:
            print(f"❌ Output file not created: {output_file}")
            return False

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_single_file()
    sys.exit(0 if success else 1)
