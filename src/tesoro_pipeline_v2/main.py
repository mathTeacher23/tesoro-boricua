#!/usr/bin/env python3
"""
Tesoro Pipeline V2 - Main Orchestrator

Complete data pipeline for processing Tesoro definitions:
0. Webscraping: Extract raw definitions (can be skipped with RUN_WEBSCRAPER=False)
1. Consolidation + Preprocessing: Consolidate definitions and transform format
2. Translation: Translate Spanish to English

All stages can be toggled on/off for iterative development.

Usage:
    python main.py                    # Full pipeline (consolidate+preprocess+translate)
    python main.py --no-translate     # Skip translation
    python main.py --consolidate      # Only consolidation+preprocessing
    python main.py --webscrape        # Only webscraping
    python main.py --translate        # Only translation (assumes preprocessing done)
    python main.py --help             # Show full usage information

Pipeline Stages:
    Stage 0: Webscraping
             Input:  Web sources (https://tesoro.pr)
             Output: ../data/raw/raw_tesoro_v2/ (raw definition JSON files)
             Script: webscraper.py
             Toggle: RUN_WEBSCRAPER = False (default, already ran)

    Stage 1A: Consolidation
             Input:  ../data/raw/raw_tesoro_v2/ (raw definitions)
             Output: ../webscrape/data/preprocessed_tesoro_v2/ (consolidated JSON files)

    Stage 1B: Preprocessing
             Input:  ../webscrape/data/preprocessed_tesoro_v2/ (consolidated definitions)
             Output: ../data/preprocessed/preprocessed_tesoro_v2/ (transformed for react_ui)

    Stage 2: Translation
             Input:  ../data/preprocessed/preprocessed_tesoro_v2/
             Output: ../data/translated/translated_tesoro_v2/ (with English translations)
             Script: translate_v2.py
"""

import sys
import subprocess
from pathlib import Path


# ============================================================================
# PIPELINE CONFIGURATION
# ============================================================================

# Set to False to skip webscraping (recommended - already scraped)
# Set to True to re-run webscraping from https://tesoro.pr
RUN_WEBSCRAPER = False


# ============================================================================
# PIPELINE FUNCTIONS
# ============================================================================

def run_webscrape():
    """Run webscraping stage."""
    print("\n" + "="*80)
    print("STAGE 0: WEBSCRAPING")
    print("="*80)
    try:
        result = subprocess.run(
            [sys.executable, "webscraper.py"],
            cwd=Path(__file__).parent,
            check=True
        )
        print("\n✅ Webscraping completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Webscraping failed: {e}")
        return False


def run_consolidate_and_preprocess():
    """Run consolidation and preprocessing stages."""
    print("\n" + "="*80)
    print("STAGES 1A-1B: CONSOLIDATION + PREPROCESSING")
    print("="*80)
    try:
        result = subprocess.run(
            [sys.executable, "preprocess_v2.py"],
            cwd=Path(__file__).parent,
            check=True
        )
        print("\n✅ Consolidation and preprocessing completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Consolidation and preprocessing failed: {e}")
        return False


def run_translate():
    """Run translation stage."""
    print("\n" + "="*80)
    print("STAGE 2: TRANSLATION")
    print("="*80)
    try:
        result = subprocess.run(
            [sys.executable, "translate_v2.py"],
            cwd=Path(__file__).parent,
            check=True
        )
        print("\n✅ Translation completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Translation failed: {e}")
        return False


def print_usage():
    """Print detailed usage information."""
    print("""
Tesoro Pipeline V2 - Orchestrator

USAGE:
  python main.py [OPTIONS]

OPTIONS:
  (none)                    Run full pipeline: consolidate → preprocess → translate
  --no-translate            Run consolidate + preprocess (skip translation)
  --consolidate             Run only consolidation and preprocessing
  --webscrape               Run only webscraping
  --translate               Run only translation (assumes preprocessing already done)
  --help                    Show this message

CONFIGURATION:

  Webscraper Toggle:
    - RUN_WEBSCRAPER = False (default): Skip webscraping (already ran once)
    - RUN_WEBSCRAPER = True: Enable webscraping (uncomment in main.py to activate)

  Data Locations:
    - Raw data:           ../data/raw/raw_tesoro_v2/
    - Consolidated data:  ../webscrape/data/preprocessed_tesoro_v2/
    - Preprocessed data:  ../data/preprocessed/preprocessed_tesoro_v2/
    - Translated data:    ../data/translated/translated_tesoro_v2/

PIPELINE OVERVIEW:

  Stage 0: Webscraping (RUN_WEBSCRAPER = False by default)
    Input:  Web sources (https://tesoro.pr)
    Process: Extract word definitions using Selenium
    Output: ../data/raw/raw_tesoro_v2/ (raw definition JSON files, 27 letter folders)
    Toggle: Set RUN_WEBSCRAPER = True to enable
    Features:
      - Per-word JSON files
      - Organized by letter (a-z, ñ)
      - Includes variants, themes, sources, years

  Stage 1A: Consolidation
    Input:  ../data/raw/raw_tesoro_v2/ (raw definitions)
    Process: Consolidate multiple definitions per word/superscript with fallback strategy
    Output: ../webscrape/data/preprocessed_tesoro_v2/ (consolidated JSON files)
    Features:
      - Longest-definition fallback when consolidation fails
      - Quality flag: could_not_consolidate (true/false)
      - Metadata: themes, sources, years, stability scores

  Stage 1B: Preprocessing
    Input:  ../webscrape/data/preprocessed_tesoro_v2/ (consolidated files)
    Process: Transform consolidated data into uniform format
    Output: ../data/preprocessed/preprocessed_tesoro_v2/ (transformed_X.json files)
    Features:
      - Fix underscores to spaces in term names
      - Group definitions by letter
      - Preserve consolidation metadata and quality flags

  Stage 2: Translation
    Input:  ../data/preprocessed/preprocessed_tesoro_v2/ (transformed definitions)
    Process: Translate Spanish definitions to English using Helsinki-NLP/opus-mt-es-en
    Output: ../data/translated/translated_tesoro_v2/ (bilingual definitions)
    Time: 2-4 hours with GPU acceleration
    Features:
      - GPU-accelerated translation
      - Batch processing for efficiency
      - Bilingual output (es_definitions + en_definitions)

WORKFLOW EXAMPLES:

  1. Run full pipeline (consolidate+preprocess+translate):
     $ python main.py

  2. Fine-tuning consolidation logic (rerun without translation):
     $ python main.py --no-translate
     (Modify consolidation logic as needed, then re-run)

  3. Re-running just translation (data already consolidated/preprocessed):
     $ python main.py --translate
     (Useful if translation was interrupted)

  4. Running webscraper (if data needs to be re-scraped):
     - Edit main.py: set RUN_WEBSCRAPER = True
     - Or: python main.py --webscrape

TOGGLEABLE STAGES:

  The main purpose of this orchestrator is to allow you to:
  - Skip webscraping (disabled by default, already ran)
  - Run consolidation+preprocessing iteratively while fine-tuning
  - Run translation separately (long-running, expensive)
  - Combine stages as needed during development

DIRECTORY STRUCTURE:

  tesoro_pipeline_v2/
  ├── main.py                 # This orchestrator
  ├── webscraper.py           # Web scraper for tesoro.pr
  ├── preprocess_v2.py        # Consolidation + preprocessing engine
  ├── translate_v2.py         # Translation engine
  ├── consolidate.py          # Core consolidation logic
  ├── validation/             # Data validation interface
  │   ├── validation_app.py   # Flask backend
  │   ├── index.html          # Web UI
  │   └── README.md
  └── [other scripts]

  ../data/
  ├── raw/
  │   └── raw_tesoro_v2/      # Raw definitions (27 letter folders)
  ├── preprocessed/
  │   └── preprocessed_tesoro_v2/  # Transformed definitions ready for translation
  └── translated/
      └── translated_tesoro_v2/    # Final bilingual definitions

  ../webscrape/data/
  └── preprocessed_tesoro_v2/     # Consolidated definitions (from consolidation phase)

VALIDATION UI:

  Run the validation interface to inspect data:
  $ cd validation
  $ python validation_app.py
  Then visit: http://localhost:5000
    """)


def main():
    """Main entry point."""

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg == "--help":
            print_usage()
            return True

        elif arg == "--webscrape":
            print("\n" + "="*80)
            print("TESORO V2 PIPELINE: Webscraping Only")
            print("="*80)
            return run_webscrape()

        elif arg == "--no-translate" or arg == "--consolidate":
            print("\n" + "="*80)
            print("TESORO V2 PIPELINE: Consolidation + Preprocessing Only")
            print("="*80)
            return run_consolidate_and_preprocess()

        elif arg == "--translate":
            print("\n" + "="*80)
            print("TESORO V2 PIPELINE: Translation Only")
            print("="*80)
            return run_translate()

        else:
            print(f"Unknown option: {arg}")
            print("Use 'python main.py --help' for usage information")
            sys.exit(1)

    # Default: run full pipeline
    print("\n" + "="*80)
    print("TESORO V2 PIPELINE: Full Pipeline")
    print("="*80)

    # Check if we should run webscraper
    if RUN_WEBSCRAPER:
        print("\nNote: RUN_WEBSCRAPER is enabled. Running webscraping first...")
        if not run_webscrape():
            print("\n❌ Pipeline failed at webscraping stage")
            return False
    else:
        print("\nNote: RUN_WEBSCRAPER is False (skipped). To enable webscraping, set RUN_WEBSCRAPER = True in main.py")

    # Stage 1: Consolidation + Preprocessing
    print("\nRunning consolidation + preprocessing...")
    if run_consolidate_and_preprocess():
        # Stage 2: Translation
        print("\nRunning translation...")
        return run_translate()
    else:
        print("\n❌ Pipeline failed at consolidation/preprocessing stage")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
