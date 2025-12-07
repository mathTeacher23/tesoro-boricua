# React UI Update - New Data Structure

## What Changed

The React UI has been updated to work with the new `letter/word.json` structure from `preprocessed_tesoro_v2` and `translated_tesoro_v2`.

### Backend Changes (`backend_server.py`)

Added new API endpoints:
- `GET /api/dictionary/letters` - Get available letters
- `GET /api/dictionary/letter/{letter}` - Get all words for a letter
- `GET /api/dictionary/word/{word}` - Get specific word details
- `GET /api/dictionary/search?query={word}&search_type={type}` - Search words

**Smart Fallback Logic:**
- For letters **a, b, c**: Uses `translated_tesoro_v2/<letter>/<word>.json` (has English translations)
- For other letters: Uses `preprocessed_tesoro_v2/<letter>/<word>.json` (Spanish only, empty `en_definitions`)

### Frontend Changes (`react_ui/src/pages/LanguagePage.js`)

Updated to:
- Fetch data from new API endpoints instead of flat JSON files
- Display English translations when available (letters a, b, c currently)
- Show Spanish-only definitions for letters without translations yet

## How to Run

### 1. Start the Backend Server

```bash
python backend_server.py
```

Server will run on `http://localhost:8000`

### 2. Start the React Dev Server

```bash
cd react_ui
npm start
```

React app will run on `http://localhost:3000`

### 3. Test the App

1. Navigate to the Language page
2. Click on letters A, B, or C - you should see **both Spanish and English** definitions
3. Click on other letters (D-Z) - you'll see **Spanish only** (English will be empty)
4. Search for words - works across all letters

## Current Status

### Translated (Has English):
- ✅ Letter A
- ✅ Letter B
- ✅ Letter C (if finished translating)

### Preprocessed Only (Spanish only):
- 📝 Letters D-Z, Ñ (will show empty `en_definitions`)

## Next Steps

Once you finish running `translator.py` on all letters:
1. All letters will automatically have English translations
2. No code changes needed - the backend automatically checks `translated_tesoro_v2` first
3. The UI will display both Spanish and English for all words

## Testing Checklist

- [ ] Backend starts without errors
- [ ] React app starts without errors
- [ ] Alphabet navigation shows available letters
- [ ] Clicking letter A/B/C shows words with English translations
- [ ] Clicking letter D+ shows words with Spanish only
- [ ] Search works across all letters
- [ ] Source filter works (Tesoro vs Dialecto)
- [ ] Translation sidebar works
- [ ] LLM chat sidebar works

## Troubleshooting

**Issue:** "Failed to fetch"
- **Solution:** Make sure backend server is running on port 8000

**Issue:** "No words found"
- **Solution:** Check that `data/preprocessed/preprocessed_tesoro_v2/<letter>/` has JSON files

**Issue:** "English definitions empty"
- **Solution:** This is expected for letters not yet translated. Run `translator.py` on those letters.
