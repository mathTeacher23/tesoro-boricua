#!/usr/bin/env python3
"""
TESORO UNIFIED PIPELINE (2025)

Combines all consolidation and preprocessing into a single script.

Major Features:
---------------
1. Semantic consolidation with embeddings
2. Clustering to detect distinct meaning groups
3. Centroid selection for representative definitions
4. Immediate preprocessing output as words are processed
5. Real-time file generation by letter and word
6. LLM-based definition polishing (optional)

Usage:
    python pipeline.py

This creates files in: data/preprocessed/preprocessed_tesoro_v2/<letter>/<word>.json

Dependencies:
    pip install sentence-transformers scikit-learn openai
"""

import json
import re
import sys
import time
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict, Counter
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

apply_clustering = True

LMSTUDIO_URL = "http://127.0.0.1:1234/v1"
LMSTUDIO_API_KEY = "lm-studio"

# Paths (reference TESORO_BORICUA level - 3 directories up from tesoro_pipeline_v2)
TESORO_ROOT = Path(__file__).parent.parent.parent
RAW_DATA_DIR = TESORO_ROOT / "data" / "raw" / "raw_tesoro_v2"
OUTPUT_DIR = TESORO_ROOT / "data" / "preprocessed" / "preprocessed_tesoro_v2"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# MODULE 1: TEXT CLEANING
# ============================================================================

class DefinitionCleaner:
    """
    Cleans raw dictionary definitions by removing:
      - Source citations
      - Parenthetical metadata
      - Example phrases
      - Grammar labels
      - Bracketed etymology notes

    Goal:
      Extract only the *meaning*, not the historical or bibliographic baggage.

    The cleaning is intentionally conservative to avoid losing real meaning.
    """

    # Common grammar labels
    GRAMMAR_LABELS = r'\b(adj\.?|adv\.?|v\.?|n\.?|sust\.?|interj\.?|prep\.?|conj\.)\b'

    def clean(self, text: str) -> str:
        if not text:
            return ""

        t = text

        # ========================================================================
        # FIX 1: PRESERVE BRACKETED CONTENT (editorial clarifications)
        # ========================================================================
        # Square brackets [...] often contain essential semantic content
        # (e.g., [embarcaciones] clarifies what type of thing is being described)
        # Remove the brackets but KEEP the content
        t = re.sub(r'\[([^\]]+)\]', r'\1', t)

        # Remove parenthetical metadata, but be selective
        # Remove obvious metadata patterns:
        # - Language/region markers: (Voz ind. ant.), (Am.), (PR.), etc.
        # - Grammar labels: (adj.), (sust.), etc.
        # - Etymology: (Del lat...), (De origen...), etc.

        # Pattern for language/region metadata
        t = re.sub(r'\([Vv]oz\s+[^)]+\)', '', t)  # (Voz ind. ant.)
        t = re.sub(r'\(Am\.\)', '', t)  # (Am.)
        t = re.sub(r'\(P\.?R\.?\)', '', t)  # (PR) or (P.R.)
        t = re.sub(r'\([Dd]el?\s+[^)]+\)', '', t)  # (Del lat...), (De origen...)
        t = re.sub(r'\([Dd]e\s+or\.\s+[^)]+\)', '', t)  # (De or. caribe)

        # Remove grammar labels in parentheses
        t = re.sub(r'\((?:adj|adv|sust|n|v|interj|prep|conj)\.?\)', '', t, flags=re.IGNORECASE)

        # Remove any remaining short parentheticals (likely metadata)
        # but keep longer ones that might contain semantic content
        t = re.sub(r'\([^)]{1,20}\)', lambda m: '' if any(
            c.isdigit() or c.isupper() for c in m.group()
        ) else m.group(), t)

        # Remove grammar labels (adj., n., etc) that appear outside parentheses
        t = re.sub(self.GRAMMAR_LABELS, '', t, flags=re.IGNORECASE)

        # Remove standalone source citations "Abbad 1788"
        t = re.sub(r'\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*(?:,\s*)?\d{4}\b', '', t)

        # Remove quotes around examples
        t = re.sub(r'"[^"]*"', '', t)

        # Collapse whitespace
        t = re.sub(r'\s+', ' ', t).strip()

        return t


# ============================================================================
# MODULE 2: SEMANTIC CONSOLIDATION
# ============================================================================

class SemanticConsolidator:
    """
    Converts cleaned definitions into embeddings and clusters them
    to determine the "main sense" and its representative definition.

    Steps:
      1. Compute sentence embeddings
      2. Cluster the definitions by similarity
      3. Select the largest cluster (dominant meaning)
      4. Compute centroid of cluster
      5. Choose definition closest to centroid (best representative)

    Returns:
      consolidated definition + full metadata + cluster map
    """

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.apply_clustering = apply_clustering


    def consolidate(self, cleaned_defs: List[str]) -> Dict[str, Any]:

        if not cleaned_defs:
            return {
                "consolidated": "",
                "issues": ["No definitions available."],
                "cleaned_definitions": []
            }

        # For single definitions we still compute stability = 1
        if len(cleaned_defs) == 1:
            return {
                "consolidated": cleaned_defs[0],
                "cluster_assignments": [0] if self.apply_clustering else None,
                "cluster_sizes": {0: 1} if self.apply_clustering else None,
                "dominant_cluster": 0 if self.apply_clustering else None,
                "stability": 1.0,
                "issues": [],
                "cleaned_definitions": cleaned_defs
            }

        # -------------------------------------------------------------
        # 1. Compute embeddings (ALWAYS, even if clustering is off)
        # -------------------------------------------------------------
        embeddings = np.array(self.model.encode(cleaned_defs))

        # Compute cosine stability (ALWAYS)
        all_sims = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                s = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
                all_sims.append(s)

        stability = float(sum(all_sims) / len(all_sims)) if all_sims else 1.0

        # -------------------------------------------------------------
        # 2. OPTIONAL CLUSTERING
        # -------------------------------------------------------------
        if not self.apply_clustering:
            return {
                "consolidated": None,                     # summarizer will produce final text
                "cluster_assignments": None,
                "cluster_sizes": None,
                "dominant_cluster": None,
                "centroid_definition": None,
                "stability": round(stability, 4),
                "issues": [],
                "cleaned_definitions": cleaned_defs,
                "definitions_for_summary": cleaned_defs    # 🔧 KEY: pass full list to summarizer
            }

        # -------------------------------------------------------------
        # 3. FULL CLUSTERING MODE (your original logic)
        # -------------------------------------------------------------
        clustering = AgglomerativeClustering(
            n_clusters=None,
            linkage='average',
            distance_threshold=0.35
        )
        labels = clustering.fit_predict(embeddings)

        cluster_sizes = {}
        for c in labels:
            cluster_sizes[c] = cluster_sizes.get(c, 0) + 1

        dominant_cluster = max(cluster_sizes, key=cluster_sizes.get)
        # -------------------------------------------------------------
        # UPGRADED CENTROID + REPRESENTATIVE SELECTION
        # -------------------------------------------------------------
        idxs = [i for i, c in enumerate(labels) if c == dominant_cluster]

        # 1. Extract cluster embeddings
        dom_embeds = embeddings[idxs]

        # 2. Normalize embeddings
        dom_embeds_norm = dom_embeds / np.linalg.norm(dom_embeds, axis=1, keepdims=True)

        # 3. Pairwise similarities
        pairwise = cosine_similarity(dom_embeds_norm)
        mean_pairwise = pairwise.mean(axis=1)

        # 4. Remove outliers (bottom 10%)
        cutoff = np.percentile(mean_pairwise, 10)
        core_mask = mean_pairwise >= cutoff

        core_embeds = dom_embeds_norm[core_mask]
        core_idxs = np.array(idxs)[core_mask]

        # If too small, fall back to full cluster
        if len(core_embeds) < 2:
            core_embeds = dom_embeds_norm
            core_idxs = np.array(idxs)
            mean_pairwise_core = mean_pairwise
        else:
            mean_pairwise_core = mean_pairwise[core_mask]

        # 5. Weighted centroid
        weights = mean_pairwise_core / mean_pairwise_core.sum()
        centroid_vec = np.sum(core_embeds * weights[:, None], axis=0)

        # 6. Hybrid representativeness score
        sims_centroid = cosine_similarity([centroid_vec], core_embeds)[0]

        # ========================================================================
        # FIX 2: BOOST NOUN-PHRASE DEFINITIONS
        # ========================================================================
        # Favor definitions that start with clear noun phrases (hypernyms)
        # These are more definitional (what it IS) rather than descriptive (what it DOES)
        noun_boost = np.zeros(len(core_idxs))

        # Common noun patterns in Spanish definitions
        noun_patterns = [
            r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:ción|miento|dad|ía|aje|eza|ura|or|ora)',  # -ción, -miento, etc.
            r'^(?:Tipo|Clase|Especie|Forma|Modo|Acto|Acción)\s+de',  # "Tipo de...", "Clase de..."
            r'^(?:Persona|Animal|Planta|Objeto|Lugar|Instrumento|Herramienta)',  # Clear nouns
            r'^(?:Embarcación|Recipiente|Utensilio|Alimento|Bebida|Árbol)',  # More clear nouns
        ]

        for i, idx in enumerate(core_idxs):
            definition = cleaned_defs[idx].strip()

            # Check if definition starts with a noun pattern
            for pattern in noun_patterns:
                if re.match(pattern, definition, re.IGNORECASE):
                    noun_boost[i] = 0.15  # 15% boost
                    break

            # Additional boost for very clear dictionary-style definitions
            # (short, starts with capital letter, no verbs in first 3 words)
            words = definition.split()
            if len(words) >= 2 and len(words) <= 20:  # Not too short, not too long
                first_three = ' '.join(words[:3]).lower()
                # Check if it doesn't start with a verb
                if not re.match(r'^[a-z]+(?:ar|er|ir|arse|erse|irse)', first_three):
                    noun_boost[i] += 0.1  # Additional 10% boost

        hybrid = 0.7 * sims_centroid + 0.3 * mean_pairwise_core + noun_boost

        best_local_index = int(np.argmax(hybrid))
        best_idx = core_idxs[best_local_index]
        centroid_def = cleaned_defs[best_idx]


        issues = []
        if len(cluster_sizes) > 1:
            issues.append("Multiple semantic clusters detected (variants differ significantly).")

        return {
            "consolidated": centroid_def,
            "cluster_assignments": labels.tolist(),
            "cluster_sizes": cluster_sizes,
            "dominant_cluster": dominant_cluster,
            "centroid_definition": centroid_def,
            "stability": round(stability, 4),
            "issues": issues,
            "cleaned_definitions": cleaned_defs,
            "definitions_for_summary": [cleaned_defs[i] for i in idxs]  # only dominant cluster
        }



# ============================================================================
# MODULE 3: HYBRID SEMANTIC SUMMARIZER
# ============================================================================

class HybridDefinitionSummarizer:
    """
    Improved hybrid summarizer using:
      - semantic head extraction
      - multi-definition blending
      - noun-first / verb-first detection
      - clean dictionary skeleton templates
    """

    VERB_START = re.compile(r'^[a-záéíóúñ]+(?:se)?\b', re.IGNORECASE)

    def is_verb_first(self, text: str) -> bool:
        tokens = text.lower().split()
        if not tokens:
            return False
        # Verb-first heuristic: first token is an infinitive or 3rd person singular ("provoca")
        return tokens[0].endswith("r") or tokens[0].endswith("arse") or tokens[0].endswith("erse")

    # ---------------------------------------------------------
    # HEAD NOUN EXTRACTION 2.0
    # ---------------------------------------------------------
    def extract_head(self, defs: List[str]) -> str:
        """
        Extract a stable semantic head by looking at patterns across all
        definitions and choosing the most common noun phrase.
        """
        heads = []

        for d in defs:
            # until punctuation
            m = re.match(r'^([^.,;:]+)', d)
            head = m.group(1).strip() if m else d
            # keep only first 6 words to avoid overly specific heads
            head = " ".join(head.split()[:6])
            heads.append(head.lower())

        # pick the shortest *mode* (most common pattern or similar)
        counts = Counter(heads)
        best = min(counts.items(), key=lambda x: ( -x[1], len(x[0]) ))[0]  # highest freq, shortest

        return best

    # ---------------------------------------------------------
    # COLLECT DESCRIPTION PHRASES ACROSS ALL DEFINITIONS
    # ---------------------------------------------------------
    def extract_description(self, defs: List[str], head: str) -> str:

        descs = []
        for d in defs:
            lower = d.lower()
            if lower.startswith(head):
                tail = lower[len(head):].strip(" .,:;")
                if len(tail.split()) >= 3:
                    descs.append(tail)

        if not descs:
            return ""

        # pick most common phrase
        counts = Counter(descs)
        return counts.most_common(1)[0][0]

    # ---------------------------------------------------------
    # MAIN ENTRYPOINT
    # ---------------------------------------------------------
    def summarize(self, definitions: List[str]) -> str:
        if not definitions:
            return ""

        # Clean and trim
        defs = [d.strip() for d in definitions if d.strip()]
        representative = defs[0]

        # Verb-first path
        if self.is_verb_first(representative):
            skeleton = self.build_verb_skeleton(defs)
        else:
            skeleton = self.build_noun_skeleton(defs)

        return self.polish_with_llm(skeleton)

    # ---------------------------------------------------------
    # VERB SKELETON
    # ---------------------------------------------------------
    def build_verb_skeleton(self, defs: List[str]) -> str:
        first = defs[0].lower()
        action = " ".join(first.split()[:4])
        return f"Acción de {action}"

    # ---------------------------------------------------------
    # NOUN SKELETON
    # ---------------------------------------------------------
    def build_noun_skeleton(self, defs: List[str]) -> str:
        head = self.extract_head(defs)
        desc = self.extract_description(defs, head)

        if desc:
            return f"{head}, {desc}"
        return head

    # ---------------------------------------------------------
    # POLISH
    # ---------------------------------------------------------
    def polish_with_llm(self, skeleton: str) -> str:
        try:
            client = OpenAI(
                base_url="http://127.0.0.1:1234/v1",
                api_key="lm-studio"
            )
            

            prompt = f"""
            Usted es lexicógrafo profesional.
            Transforme la siguiente estructura en una definición breve,
            clara y neutra, sin agregar nuevos significados.

            Texto: "{skeleton}"
            Salida: una sola oración, tono de diccionario.
            """

            resp = client.chat.completions.create(
                model="meta-llama-3.1-8b-instruct",
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )

            return resp.choices[0].message.content.strip()

        except Exception:
            return skeleton



# ============================================================================
# MODULE 4: MAIN ENGINE (FILES + SUPERSCRIPTS)
# ============================================================================

class DefinitionConsolidator:
    """
    High-level orchestrator:
      - Loads the dictionary JSON
      - Extracts definitions by superscript
      - Cleans them
      - Runs semantic consolidation
      - Runs hybrid summarization
      - Records benchmarks
      - Produces a detailed report
    """

    def __init__(self, input_file: str):
        with open(input_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.words = list(self.data.keys())
        self.cleaner = DefinitionCleaner()
        self.semantic = SemanticConsolidator()
        self.summarizer = HybridDefinitionSummarizer()
        self.reviewer_client = OpenAI(
            base_url=LMSTUDIO_URL,
            api_key=LMSTUDIO_API_KEY
        )

    def _translate_definition(self, es_definition: str) -> str:
        """
        Translate Spanish definition to English using the local LLM.
        Uses the consolidator model (meta-llama-3.1-8b-instruct) which is good at Spanish/English.

        Args:
            es_definition: Spanish definition to translate

        Returns:
            English translation
        """
        if not es_definition or not es_definition.strip():
            return ""

        prompt = f"""
        Eres un traductor profesional especializado en español puertorriqueño e inglés.

        Traduce la siguiente definición de diccionario del español al inglés.
        Mantén el tono formal y académico de un diccionario.

        DEFINICIÓN EN ESPAÑOL:
        {es_definition}

        INSTRUCCIONES:
        - Traduce con precisión, manteniendo el significado exacto
        - Usa vocabulario formal y apropiado para un diccionario
        - Si hay términos culturales específicos de Puerto Rico, tradúcelos pero preserva el contexto
        - NO agregues explicaciones, SOLO la traducción

        Salida: SOLO la definición traducida al inglés, sin comillas ni comentarios adicionales.
        """

        try:
            resp = self.reviewer_client.chat.completions.create(
                model="meta-llama-3.1-8b-instruct",  # Same model, good at Spanish/English
                messages=[
                    {"role": "system", "content": "You are a professional translator specializing in Spanish to English dictionary translations."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
                temperature=0.1,  # Low temperature for consistent translations
            )
            result = resp.choices[0].message.content.strip()

            # Remove surrounding quotes if the LLM wrapped the response
            if result.startswith('"') and result.endswith('"'):
                result = result[1:-1]
            elif result.startswith("'") and result.endswith("'"):
                result = result[1:-1]

            return result

        except Exception as e:
            print(f"⚠️ Translation failed: {e}")
            return ""

    def _review_definition(self, cleaned_defs: List[str], summary: str) -> str:
        """
        Use the reviewer LLM to validate and refine the consolidated definition.
        Returns a corrected definition OR the original summary if no issues found.
        """
        if not summary:
            return summary

        # ========================================================================
        # FIX 3: STRENGTHENED REVIEWER PROMPT
        # ========================================================================
        # Explicit instructions to preserve core concepts and hypernyms
        prompt = f"""
        Eres un revisor lexicográfico profesional experto en diccionarios.

        Tu tarea: validar y corregir una definición consolidada comparándola
        contra las definiciones originales del diccionario.

        DEFINICIONES ORIGINALES DEL DICCIONARIO:
        {json.dumps(cleaned_defs, ensure_ascii=False, indent=2)}

        DEFINICIÓN CONSOLIDADA (a revisar):
        {summary}

        INSTRUCCIONES CRÍTICAS - Verifica en este orden:

        1. CONCEPTO NÚCLEO (MÁS IMPORTANTE):
           - ¿La definición dice QUÉ ES el término? (no solo qué hace)
           - ¿Incluye el HIPERÓNIMO o CATEGORÍA? (ej: "embarcación", "tipo de", "persona que")
           - Si las definiciones originales mencionan la categoría (sustantivo, objeto, etc.),
             la definición consolidada DEBE incluirla

        2. INFORMACIÓN ESENCIAL:
           - ¿Falta información crucial presente en VARIAS definiciones originales?
           - ¿Se perdieron características definitorias importantes?

        3. EXACTITUD:
           - ¿Hay contradicciones con las definiciones originales?
           - ¿Se inventó significado nuevo que no está en las originales?

        4. CLARIDAD:
           - ¿Es repetitiva o confusa?
           - ¿Usa lenguaje de diccionario apropiado?

        REGLAS ESTRICTAS:
        - Si falta el hiperónimo/categoría pero está en las originales: AGRÉGALO
        - Prioriza "qué es" sobre "qué hace" o "para qué sirve"
        - Mantén el tono neutral de diccionario
        - Una sola oración clara y completa

        Salida: SOLO la definición mejorada (o la original si ya es perfecta).
        NO expliques, NO agregues comentarios, SOLO la definición.
        """

        try:
            resp = self.reviewer_client.chat.completions.create(
                model="qwen2.5-7b-instruct",
                messages=[
                    {"role": "system", "content": "Eres un revisor lexicográfico experto que prioriza la precisión conceptual sobre todo."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=250,
                temperature=0.1,  # Lower temperature for more consistent output
            )
            result = resp.choices[0].message.content.strip()

            # Remove surrounding quotes if the LLM wrapped the response in them
            if result.startswith('"') and result.endswith('"'):
                result = result[1:-1]
            elif result.startswith("'") and result.endswith("'"):
                result = result[1:-1]

            return result

        except Exception as e:
            print(f"⚠️ Reviewer failed: {e}")
            return summary


    def run(self) -> Dict[str, Any]:
        full_report = {}

        for word in self.words:
            defs_by_sup = self._extract_definitions_by_superscript(word)
            word_report = {}

            for sup, def_items in defs_by_sup.items():
                start = time.time()

                # Extract text from the new structure
                raw_defs = [item['text'] for item in def_items]

                # ============================================================
                # OPTIMIZATION: Skip LLM consolidation when not needed
                # ============================================================
                skip_consolidation = False
                skip_reason = None
                selected_def = None
                selected_item = None

                # Case 1: Single definition - use it directly
                if len(def_items) == 1:
                    skip_consolidation = True
                    skip_reason = "single_definition"
                    selected_def = def_items[0]['text']
                    selected_item = def_items[0]['full_item']

                # Case 2: Multiple definitions but has recent sources (>= 1995)
                elif len(def_items) > 1:
                    # Filter definitions with year >= 1995
                    recent_defs = [item for item in def_items if item['year'] and item['year'] >= 1995]

                    if recent_defs:
                        # Use the latest definition (highest year)
                        latest_item = max(recent_defs, key=lambda x: x['year'])
                        skip_consolidation = True
                        skip_reason = f"recent_definition_from_{latest_item['year']}"
                        selected_def = latest_item['text']
                        selected_item = latest_item['full_item']

                # ============================================================
                # If skipping consolidation, create a minimal result
                # ============================================================
                if skip_consolidation:
                    cleaned_def = self.cleaner.clean(selected_def)
                    semantic_result = {
                        "consolidated": cleaned_def,
                        "final_definition": cleaned_def,
                        "hybrid_summary": cleaned_def,
                        "cluster_assignments": None,
                        "cluster_sizes": None,
                        "dominant_cluster": None,
                        "stability": 1.0,
                        "issues": [],
                        "cleaned_definitions": [cleaned_def],
                        "raw_definition_count": len(raw_defs),
                        "cleaned_definition_count": 1,
                        "skipped_consolidation": True,
                        "skip_reason": skip_reason,
                        "selected_definition_metadata": {
                            "year": selected_item.get('year') if selected_item else None,
                            "source": selected_item.get('source') if selected_item else None,
                        }
                    }
                    end = time.time()
                    semantic_result["benchmark_time_sec"] = round(end - start, 3)

                # ============================================================
                # Otherwise, run full consolidation pipeline
                # ============================================================
                else:
                    cleaned = [self.cleaner.clean(d) for d in raw_defs if d.strip()]
                    semantic_result = self.semantic.consolidate(cleaned)

                    # NEW: hybrid summarization
                    defs_for_summary = semantic_result.get("definitions_for_summary", cleaned)
                    semantic_result["hybrid_summary"] = self.summarizer.summarize(defs_for_summary)
                    # REVIEWER STEP
                    reviewed = self._review_definition(
                        cleaned,
                        semantic_result["hybrid_summary"]
                    )
                    semantic_result["final_definition"] = reviewed

                    end = time.time()
                    semantic_result["benchmark_time_sec"] = round(end - start, 3)
                    semantic_result["raw_definition_count"] = len(raw_defs)
                    semantic_result["cleaned_definition_count"] = len(cleaned)
                    semantic_result["skipped_consolidation"] = False

                # ============================================================
                # TRANSLATION: Always translate the final definition
                # ============================================================
                es_definition = semantic_result.get("final_definition", "")
                en_definition = self._translate_definition(es_definition)
                semantic_result["en_definition"] = en_definition

                word_report[sup] = semantic_result

            full_report[word] = word_report

        return full_report

    def _extract_definitions_by_superscript(self, word: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract definitions organized by superscript from raw JSON data.

        Args:
            word: The word key in self.data (can be with underscores or spaces)

        Returns:
            Dictionary mapping superscript → list of definition dicts with metadata
            Example: {"1": [{"text": "def1", "year": 2000, "source": "X", "full_item": {...}}, ...]}
        """
        defs_by_sup = defaultdict(list)

        # The word parameter might have underscores, but the actual key in JSON uses spaces
        # Try both formats: with underscores and with spaces
        word_key = word
        if word_key not in self.data:
            # Try replacing underscores with spaces
            word_key_with_spaces = word.replace('_', ' ')
            if word_key_with_spaces in self.data:
                word_key = word_key_with_spaces

        # Get the list of entries for this word from self.data
        entries = self.data.get(word_key, [])

        if not entries:
            return {}

        # Process each entry
        for entry in entries:
            superscript = str(entry.get('superscript', '1'))
            details = entry.get('details', {})
            definition_list = details.get('definition_list', [])

            # Extract definition text from nested structure
            for def_item in definition_list:
                definition_sublist = def_item.get('definition_sublist', [])
                for sub_item in definition_sublist:
                    # Use 'definition' field which contains the actual definition text
                    text = sub_item.get('definition', '')
                    if text:
                        # Extract year and convert to int if possible
                        year_raw = sub_item.get('year', '')
                        year = None
                        if year_raw:
                            try:
                                year = int(year_raw)
                            except (ValueError, TypeError):
                                pass

                        defs_by_sup[superscript].append({
                            'text': text,
                            'year': year,
                            'source': sub_item.get('source', ''),
                            'full_item': sub_item
                        })

        return dict(defs_by_sup)


# ============================================================================
# MODULE 5: PREPROCESSING & OUTPUT
# ============================================================================

def write_preprocessed_word(letter: str, word: str, raw_data: dict, consolidated_report: dict) -> bool:
    """
    Write preprocessed JSON for a single word.

    Args:
        letter: Single letter (a-z, ñ)
        word: Word name with underscores
        raw_data: The raw JSON data loaded from raw file
        consolidated_report: The consolidation report from DefinitionConsolidator

    Returns:
        True if successful
    """
    output_letter_dir = OUTPUT_DIR / letter.lower()
    output_letter_dir.mkdir(parents=True, exist_ok=True)

    term = word.replace("_", " ")

    entry = {
        "letter": letter.upper(),
        "term": term,
        "superscripts": {},
        "es_definitions": [],
        "en_definitions": [],
        "source": "https://tesoro.pr",
    }

    # Build superscript data from consolidated_report
    for word_key, superscripts_report in consolidated_report.items():
        for superscript, result in superscripts_report.items():
            # Extract metadata from raw data
            all_themes = []
            all_sources = set()
            all_years = set()
            grammar = []
            origin = None
            related_words = []

            raw_entries = raw_data.get(word_key, [])
            for entry_item in raw_entries:
                if str(entry_item['superscript']) == str(superscript):
                    details = entry_item.get('details', {})
                    grammar = details.get('grammar', [])
                    origin = details.get('origin')
                    related_words = details.get('relatedWords', [])

                    for def_item in details.get('definition_list', []):
                        for sub_item in def_item.get('definition_sublist', []):
                            if sub_item.get('themes'):
                                all_themes.extend(sub_item['themes'])
                            if sub_item.get('source'):
                                all_sources.add((sub_item['source'], sub_item.get('year', '')))
                            if sub_item.get('year'):
                                try:
                                    all_years.add(int(sub_item['year']))
                                except (ValueError, TypeError):
                                    pass

            # Count themes and get top 3
            theme_counts = Counter(all_themes)
            consolidated_themes = [theme for theme, count in theme_counts.most_common(3)]
            all_themes_found = sorted(list(set(all_themes)))

            # Format sources
            sources = [{'source': src, 'year': year} for src, year in sorted(all_sources)]

            # Get consolidated definition (Spanish)
            consolidated_def = (
                result.get('final_definition')
                or result.get('hybrid_summary')
                or result.get('consolidated')
                or result.get('centroid_definition')
                or ''
            )
            stability_score = result.get('stability', 0.0)

            # Get English translation
            en_consolidated_def = result.get('en_definition', '')

            # Determine consolidation reason if it failed
            consolidation_reason = None
            if len(consolidated_def) == 0:
                # Explain why consolidation failed
                if result.get('raw_definition_count', 0) == 0:
                    consolidation_reason = "No definitions available to consolidate"
                elif result.get('cleaned_definition_count', 0) == 0:
                    consolidation_reason = "All definitions were empty or only whitespace after cleaning"
                else:
                    consolidation_reason = "Failed to select a representative definition from cluster"

            # Get cluster count (number of unique clusters found)
            cluster_sizes = result.get('cluster_sizes')
            cluster_count = len(cluster_sizes) if cluster_sizes is not None else None

            # Get all cleaned definitions as reference (all definitions that were analyzed)
            cleaned_defs = result.get('cleaned_definitions', [])

            # Check if consolidation was skipped (optimization)
            consolidation_skipped = result.get('skipped_consolidation', False)
            consolidation_skip_reason = result.get('skip_reason', None)

            entry["superscripts"][superscript] = {
                "consolidated_definition": consolidated_def,
                "en_consolidated_definition": en_consolidated_def,  # Add English translation
                "could_not_consolidate": len(consolidated_def) == 0,
                "consolidation_reason": consolidation_reason,
                "consolidation_skipped": consolidation_skipped,  # NEW: Show if optimization was applied
                "consolidation_skip_reason": consolidation_skip_reason,  # NEW: Why it was skipped
                "consolidation_metadata": {
                    "num_definitions_analyzed": result.get('raw_definition_count', 0),
                    "num_cleaned_definitions": result.get('cleaned_definition_count', 0),
                    "definition_stability": f"Stability: {stability_score}" if stability_score else 'Unknown',
                    "semantic_similarity_score": stability_score,
                    "cluster_count": cluster_count,
                    "grammar": grammar,
                    "themes": consolidated_themes,
                    "all_themes_found": all_themes_found,
                    "sources": sources,
                    "years": sorted(list(all_years)),
                    "origin": origin,
                    "related_words": related_words,
                    "reference_definitions": cleaned_defs  # All cleaned definitions analyzed for consolidation
                }
            }
            entry["es_definitions"].append(consolidated_def)
            entry["en_definitions"].append(en_consolidated_def)  # Add English translation to main array

    # Write the file
    output_file = output_letter_dir / f"{word}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)

    return True


# ============================================================================
# MODULE 6: MAIN PIPELINE
# ============================================================================

def process_all_letters():
    """Process all letters, consolidating and preprocessing in one pass."""
    print("\n" + "="*80)
    print("TESORO UNIFIED PIPELINE: Consolidation + Preprocessing")
    print("="*80)

    if not RAW_DATA_DIR.exists():
        print(f"❌ Raw data directory not found: {RAW_DATA_DIR}")
        return False

    alphabet = list("abcdefghijklmnopqrstuvwxyz") + ["ñ"]

    for letter in alphabet:
        raw_path = RAW_DATA_DIR / letter

        if not raw_path.exists():
            print(f"⚠️  Skipping letter {letter.upper()}: folder not found")
            continue

        json_files = sorted(raw_path.glob("*.json"))

        if not json_files:
            print(f"⚠️  Skipping letter {letter.upper()}: no JSON files")
            continue

        print(f"\n{'='*80}")
        print(f"PROCESSING LETTER '{letter.upper()}' - {len(json_files)} words")
        print(f"{'='*80}\n")

        processed = 0
        failed = 0

        for idx, json_file in enumerate(json_files, 1):
            try:
                word = json_file.stem
                print(f"  [{idx:>4}/{len(json_files)}] {word}...", end=" ", flush=True)

                # CONSOLIDATE
                consolidator = DefinitionConsolidator(str(json_file))
                consolidated_report = consolidator.run()

                # LOAD RAW DATA
                with open(json_file, 'r', encoding='utf-8') as rf:
                    raw_data = json.load(rf)

                # PREPROCESS & WRITE IMMEDIATELY
                write_preprocessed_word(letter, word, raw_data, consolidated_report)

                print("✅")
                processed += 1

            except Exception as e:
                print(f"❌ Error: {str(e)}")
                failed += 1
                import traceback
                traceback.print_exc()

        print(f"\n{'='*80}")
        print(f"LETTER '{letter.upper()}' COMPLETE")
        print(f"{'='*80}")
        print(f"  Processed: {processed}")
        print(f"  Failed:    {failed}")
        print()

    return True


if __name__ == "__main__":
    success = process_all_letters()
    sys.exit(0 if success else 1)
