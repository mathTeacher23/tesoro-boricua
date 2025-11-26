#!/usr/bin/env python3
"""
Tesoro Boricua Backend API Server
Provides translation and LLM chat functionality using FastAPI and LangChain.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from translate import Translator
from langchain_community.llms import LlamaCpp
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tesoro Boricua API", version="1.0.0")

# Initialize LLM (LM Studio connection)
try:
    from langchain_openai import ChatOpenAI
    # Using OpenAI-compatible endpoint from LM Studio
    llm = ChatOpenAI(
        model="meta-llama-3.1-8b-instruct",
        api_key="not-needed",  # LM Studio doesn't require API key
        base_url="http://127.0.0.1:1234/v1",  # LM Studio OpenAI-compatible endpoint
        temperature=0.7,
    )
    logger.info("✓ LM Studio LLM initialized successfully")
except Exception as e:
    logger.warning(f"⚠️ Could not initialize LM Studio LLM: {e}")
    logger.warning(f"⚠️ Error details: {str(e)}")
    llm = None

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

class ChatRequest(BaseModel):
    message: str
    context: str = "You are a helpful assistant about Puerto Rican culture and cuisine."

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

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

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_llm(request: ChatRequest):
    """
    Chat with the LLM via LangChain using LM Studio.
    """
    if llm is None:
        raise HTTPException(
            status_code=503,
            detail="LM Studio LLM is not available. Make sure LM Studio is running on port 1234."
        )

    try:
        message = request.message.strip()
        if not message:
            raise HTTPException(status_code=400, detail="Empty message provided")

        context = request.context

        # Import message classes
        from langchain_core.messages import SystemMessage, HumanMessage

        # Create messages for ChatOpenAI
        messages = [
            SystemMessage(content=context),
            HumanMessage(content=message)
        ]

        # Call the LLM
        logger.info(f"Sending to LLM: {message[:100]}...")
        response = llm.invoke(messages)

        # Extract text from response
        response_text = response.content if hasattr(response, 'content') else str(response)

        logger.info(f"LLM Response: {response_text[:100]}...")

        return ChatResponse(
            response=response_text.strip(),
            status="success"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

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