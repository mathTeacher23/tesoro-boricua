#!/usr/bin/env python3
"""
Translation API server for Tesoro Boricua React UI.
Provides live translation between English and Spanish using FastAPI.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from translate import Translator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tesoro Boricua Translation API", version="1.0.0")

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranslationRequest(BaseModel):
    text: str
    from_lang: str = "auto"
    to_lang: str = "en"

class TranslationResponse(BaseModel):
    translated_text: str
    from_lang: str
    to_lang: str
    original_text: str

class LanguageInfo(BaseModel):
    code: str
    name: str

@app.post("/api/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate text between English and Spanish.
    """
    try:
        text = request.text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Empty text provided")

        from_lang = request.from_lang
        to_lang = request.to_lang

        # Validate language codes
        valid_langs = ['en', 'es', 'auto']
        if from_lang not in valid_langs or to_lang not in valid_langs:
            raise HTTPException(
                status_code=400,
                detail="Invalid language code. Use: en, es, or auto"
            )

        # Don't translate if source and target are the same
        if from_lang == to_lang and from_lang != 'auto':
            return TranslationResponse(
                translated_text=text,
                from_lang=from_lang,
                to_lang=to_lang,
                original_text=text
            )

        # Create translator
        translator = Translator(
            to_lang=to_lang,
            from_lang=from_lang if from_lang != 'auto' else None
        )

        # Perform translation
        translated = translator.translate(text)

        logger.info(f"Translated '{text}' from {from_lang} to {to_lang}: '{translated}'")

        return TranslationResponse(
            translated_text=translated,
            from_lang=from_lang,
            to_lang=to_lang,
            original_text=text
        )

    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "translation_api"}

@app.get("/api/supported-languages")
async def supported_languages():
    """Return supported language codes."""
    return {
        "languages": [
            LanguageInfo(code="en", name="English"),
            LanguageInfo(code="es", name="Spanish")
        ]
    }

if __name__ == "__main__":
    import uvicorn

    print("🇵🇷 Starting Tesoro Boricua Translation API...")
    print("📍 Server will run on http://localhost:8000")
    print("🔗 Translation endpoint: POST /api/translate")
    print("📚 API docs: http://localhost:8000/docs")
    print("💡 Required packages: pip install fastapi uvicorn translate")

    uvicorn.run(
        "backend_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )