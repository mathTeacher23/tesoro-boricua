#!/usr/bin/env python3
"""
TESORO Boricua Word Validation App
Compares raw and preprocessed word data side-by-side
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Data directories - find TESORO_BORICUA root by looking for data directories
def find_tesoro_root():
    current = Path(__file__).parent
    for _ in range(10):  # Search up to 10 levels
        if (current / "data" / "raw" / "raw_tesoro_v2").exists():
            return current
        current = current.parent
    # Fallback to manual path
    return Path("/Users/andrewcasanova/Documents/data_science_projects/ai_projects/TESORO_BORICUA")

BASE_DIR = find_tesoro_root()
RAW_DATA_DIR = BASE_DIR / "data" / "raw" / "raw_tesoro_v2"
PREPROCESSED_DATA_DIR = BASE_DIR / "data" / "preprocessed" / "preprocessed_tesoro_v2"

logger.info(f"BASE_DIR: {BASE_DIR}")
logger.info(f"RAW_DATA_DIR exists: {RAW_DATA_DIR.exists()}")
logger.info(f"PREPROCESSED_DATA_DIR exists: {PREPROCESSED_DATA_DIR.exists()}")

# Cache for preprocessed data
preprocessed_cache = {}


def load_preprocessed_data(word):
    """Load preprocessed data for a specific word"""
    letter = word[0].lower()
    if letter not in 'abcdefghijklmnopqrstuvwxyzñ':
        return None

    # Replace spaces with underscores in filename
    filename = word.lower().replace(' ', '_') + '.json'
    file_path = PREPROCESSED_DATA_DIR / letter / filename

    if not file_path.exists():
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading preprocessed data for {word}: {e}")
        return None


def load_raw_data(word):
    """Load raw data for a specific word"""
    letter = word[0].lower()
    if letter not in 'abcdefghijklmnopqrstuvwxyzñ':
        return None

    # Replace spaces with underscores in filename
    filename = word.lower().replace(' ', '_') + '.json'
    file_path = RAW_DATA_DIR / letter / filename

    if not file_path.exists():
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading raw data for {word}: {e}")
        return None


def get_all_words_for_letter(letter):
    """Get all words starting with a given letter from raw data"""
    letter_dir = RAW_DATA_DIR / letter.lower()
    if not letter_dir.exists():
        return []

    words = []
    try:
        for file in sorted(letter_dir.glob('*.json')):
            word = file.stem  # filename without .json
            words.append(word.replace('_', ' '))
    except Exception as e:
        logger.error(f"Error listing words for letter {letter}: {e}")

    return words


@app.route('/api/letters', methods=['GET'])
def get_letters():
    """Get all available letters"""
    letters = list('abcdefghijklmnopqrstuvwxyzñ')
    logger.info(f"Returning {len(letters)} letters")
    return jsonify({'letters': letters})


@app.route('/api/words/<letter>', methods=['GET'])
def get_words_by_letter(letter):
    """Get all words for a given letter"""
    if letter.lower() not in 'abcdefghijklmnopqrstuvwxyzñ':
        return jsonify({'error': 'Invalid letter'}), 400

    words = get_all_words_for_letter(letter.lower())
    logger.info(f"Retrieved {len(words)} words for letter '{letter}'")
    return jsonify({'words': words})


@app.route('/api/search', methods=['GET'])
def search_words():
    """Search for words by term"""
    term = request.args.get('term', '').strip()
    if not term:
        return jsonify({'error': 'Search term required'}), 400

    letter = term[0].lower()
    if letter not in 'abcdefghijklmnopqrstuvwxyzñ':
        return jsonify({'error': 'Invalid starting letter'}), 400

    # Get all words starting with the same letter that match the search
    all_words = get_all_words_for_letter(letter)
    matching_words = [w for w in all_words if term.lower() in w.lower()]

    return jsonify({'matches': matching_words[:20]})  # Limit to 20 results


@app.route('/api/word-data', methods=['GET'])
def get_word_data():
    """Get both raw and preprocessed data for a word"""
    word = request.args.get('word', '').strip()
    if not word:
        return jsonify({'error': 'Word required'}), 400

    letter = word[0].lower()
    if letter not in 'abcdefghijklmnopqrstuvwxyzñ':
        return jsonify({'error': 'Invalid starting letter'}), 400

    # Get raw data
    raw_data = load_raw_data(word)

    # Get preprocessed data (individual word file)
    preprocessed_data = load_preprocessed_data(word)

    return jsonify({
        'word': word,
        'raw': raw_data,
        'preprocessed': preprocessed_data
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    # Check data directories exist
    if not RAW_DATA_DIR.exists():
        logger.error(f"Raw data directory not found: {RAW_DATA_DIR}")
    if not PREPROCESSED_DATA_DIR.exists():
        logger.error(f"Preprocessed data directory not found: {PREPROCESSED_DATA_DIR}")

    app.run(debug=True, port=5001, host='127.0.0.1')
