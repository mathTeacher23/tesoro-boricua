# 🤖 LLM Chat Setup Guide

This guide explains how to set up and use the LLM chat feature with your Tesoro Boricua app.

## Prerequisites

You need:
1. **LM Studio** installed and running
2. **meta-llama-3.1-8b-instruct** model loaded in LM Studio
3. **Tesoro Boricua** backend running

## Step 1: Start LM Studio

1. Open LM Studio
2. Load the **meta-llama-3.1-8b-instruct** model
3. Start the local server (it runs on `http://localhost:1234` by default)
4. You should see output like: `Server listening on http://localhost:1234`

## Step 2: Install Dependencies

Run this command to install LangChain and related packages:

```bash
uv sync
```

Or if using pip:

```bash
pip install -r requirements.txt
```

## Step 3: Start Tesoro Boricua

```bash
make start
```

This will:
- Start the backend with LLM support
- Start the React frontend

## Step 4: Use the Chat Feature

1. Go to the **Language & Words** page (📖 menu)
2. Look for the **Chat** button on the left side of the screen
3. Click it to open the LLM chat sidebar
4. Type your message and hit **Send** (or Shift+Enter for new line)
5. Wait for the LLM to respond

## Example Questions

Try asking:
- "Tell me about Puerto Rican culture"
- "What are some traditional Puerto Rican dishes?"
- "How do you say hello in Spanish?"
- "What's the history of Puerto Rico?"

## Troubleshooting

### "Failed to connect to LLM"
**Problem**: Chat shows error about LM Studio not running
**Solution**:
1. Make sure LM Studio is running
2. Check that the server is on port 1234
3. Load the meta-llama-3.1-8b-instruct model
4. Restart the backend: `Ctrl+C` and `make start`

### "LM Studio not available" in logs
**Problem**: Backend logs show LM Studio warning
**Solution**:
1. Start LM Studio before starting the backend
2. Load the model
3. Start the local server in LM Studio
4. Then restart the backend

### Slow responses
**Problem**: Chat takes a long time to respond
**Solution**:
- This is normal! LLMs take time to generate responses
- Larger models are slower but more capable
- Be patient, especially on first response

### Port already in use
**Problem**: Error about port 1234 in use
**Solution**:
- Change LM Studio port to something else
- Update the backend URL in `backend_server.py` line 26:
  ```python
  base_url="http://localhost:YOUR_PORT"
  ```

## How It Works

1. **React Frontend** → User types message in chat sidebar
2. **REST API** → Message sent to backend at `/api/chat`
3. **Backend (FastAPI)** → Message forwarded to LM Studio via LangChain
4. **LM Studio** → LLM generates response using Ollama API
5. **Backend** → Response returned to frontend
6. **React Frontend** → Response displayed in chat

## Architecture

```
┌──────────────┐
│  React App   │
│  (Port 3000) │
└──────┬───────┘
       │ HTTP POST /api/chat
       ▼
┌──────────────────┐
│  FastAPI Backend │
│  (Port 8000)     │
└──────┬───────────┘
       │ HTTP (LangChain)
       ▼
┌──────────────────┐
│  LM Studio       │
│  (Port 1234)     │
└──────┬───────────┘
       │ Ollama API
       ▼
┌──────────────────┐
│  LLM Model       │
│  (Llama 3.1)     │
└──────────────────┘
```

## Customization

### Change the System Prompt

Edit `react_ui/src/components/LLMChatSidebar.tsx` line 45:

```tsx
context: 'Your custom system prompt here'
```

### Change the Model

Edit `backend_server.py` line 26:

```python
model="your-model-name"
```

### Change LM Studio Port

Edit `backend_server.py` line 27:

```python
base_url="http://localhost:YOUR_PORT"
```

## Features

✅ Chat history in sidebar
✅ Clear chat history
✅ Error handling
✅ Loading state
✅ Character limit (500 chars)
✅ Puerto Rican culture context
✅ Markdown-like formatting support

## Performance Tips

1. **Use CPU/GPU acceleration** in LM Studio for faster responses
2. **Quantized models** are faster (8-bit vs 16-bit)
3. **Smaller models** are faster but less capable
4. **Local inference** is privacy-friendly but slower than cloud APIs

## Next Steps

- Enhance with conversation memory/context
- Add streaming responses (real-time token generation)
- Store conversation history in database
- Add multiple conversation support
- Integrate with recipe recommendations

Enjoy chatting with your local LLM! 🤖✨
