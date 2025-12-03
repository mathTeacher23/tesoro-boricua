#!/usr/bin/env python3
"""
Diagnostic script to trace what happens to 'piragua' during cleaning and consolidation.
"""

import json
from pathlib import Path
from preprocess import DefinitionCleaner, SemanticConsolidator, HybridDefinitionSummarizer

# Load piragua data
TESORO_ROOT = Path(__file__).parent.parent.parent
piragua_file = TESORO_ROOT / "data" / "raw" / "raw_tesoro_v2" / "p" / "piragua.json"

with open(piragua_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get superscript 1 definitions
superscript_1 = [e for e in data['piragua'] if e['superscript'] == '1'][0]
definitions = []

for def_item in superscript_1['details']['definition_list']:
    for sub_item in def_item['definition_sublist']:
        definitions.append(sub_item['definition'])

print("="*80)
print("PIRAGUA SUPERSCRIPT 1 DIAGNOSTIC")
print("="*80)

print("\n1. RAW DEFINITIONS:")
print("-" * 80)
for i, d in enumerate(definitions, 1):
    print(f"  {i}. {d}")
    print()

# Clean definitions
cleaner = DefinitionCleaner()
cleaned = [cleaner.clean(d) for d in definitions]

print("\n2. CLEANED DEFINITIONS:")
print("-" * 80)
for i, d in enumerate(cleaned, 1):
    print(f"  {i}. {d}")
    print()

# Show what was removed
print("\n3. WHAT WAS REMOVED:")
print("-" * 80)
for i, (raw, clean) in enumerate(zip(definitions, cleaned), 1):
    if raw != clean:
        print(f"  Definition {i}:")
        print(f"    BEFORE: {raw}")
        print(f"    AFTER:  {clean}")
        print()

# Consolidate
consolidator = SemanticConsolidator()
result = consolidator.consolidate(cleaned)

print("\n4. CONSOLIDATION RESULT:")
print("-" * 80)
print(f"  Consolidated definition: {result.get('consolidated', 'N/A')}")
print(f"  Stability: {result.get('stability', 0.0)}")

# Summarize
summarizer = HybridDefinitionSummarizer()
defs_for_summary = result.get("definitions_for_summary", cleaned)
summary = summarizer.summarize(defs_for_summary)

print("\n5. HYBRID SUMMARY:")
print("-" * 80)
print(f"  {summary}")

print("\n" + "="*80)
print("KEY ISSUE: Does 'embarcación' appear anywhere after cleaning?")
print("="*80)

has_embarcacion = any('embarcación' in c.lower() or 'embarcacion' in c.lower() for c in cleaned)
print(f"  Found in cleaned definitions: {has_embarcacion}")

if not has_embarcacion:
    print("\n  ❌ PROBLEM IDENTIFIED:")
    print("  The word 'embarcación' was removed during cleaning!")
    print("  This is because it appears in brackets [embarcaciones] in the raw data.")
    print("  The DefinitionCleaner.clean() method removes ALL bracketed content.")
