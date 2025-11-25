# 🇵🇷 Tesoro Boricua - Quick Start Guide

## Getting Started in 3 Steps

### Step 1: Install Dependencies (One-time setup)
```bash
make install
```

This installs both:
- Backend dependencies (FastAPI, Uvicorn, Translate library)
- Frontend dependencies (React, React Router, etc.)

### Step 2: Start the Application
```bash
make start
```

This command will:
- Start the backend server on `http://localhost:8000`
- Start the frontend on `http://localhost:3000`
- Automatically open your browser to the React app

Both services will be running in the same terminal. Press `Ctrl+C` to stop both.

### Step 3: Access the App
- **Main App**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

---

## Available Commands

### 🚀 Most Common
```bash
make start      # Start both backend and frontend together (recommended!)
```

### 🔧 Individual Services
```bash
make backend    # Start only backend server
make frontend   # Start only React frontend
make dev        # Start in dev mode with live reload
```

### 📦 Setup & Installation
```bash
make install    # Install all dependencies
make setup      # Full setup with verification
```

### 🧹 Maintenance
```bash
make stop       # Stop all running services
make clean      # Clean build files and cache
make build      # Build production bundle
make help       # Show all available commands
```

---

## Troubleshooting

### "Failed to fetch" on Translation Feature
This means the backend server is not running. Make sure you're using `make start` to launch both services.

### Port Already in Use
If port 3000 or 8000 is in use, you can modify the Makefile:
```makefile
FRONTEND_PORT := 3001    # Change from 3000
BACKEND_PORT := 8001     # Change from 8000
```

### Dependencies Not Installing
Make sure you have:
- Python 3.7+ installed
- Node.js 14+ and npm installed

Check versions:
```bash
python3 --version
node --version
npm --version
```

### "make: command not found"
On macOS, Make should be pre-installed. On Linux, install with:
```bash
sudo apt-get install make
```

On Windows, use [GNU Make for Windows](http://gnuwin32.sourceforge.net/packages/make.htm) or use the individual commands.

---

## Project Structure

```
TESORO_BORICUA/
├── Makefile                    # All automation commands
├── .env.example                # Environment variables template
├── backend_server.py           # FastAPI server for translations
├── react_ui/                   # React frontend
│   ├── package.json
│   ├── public/
│   ├── src/
│   └── ...
└── ...
```

---

## What's Running

### Backend (http://localhost:8000)
- FastAPI server
- Translation API endpoint: `/api/translate`
- API Documentation: `/docs` (Swagger UI)
- Health check: `/api/health`

### Frontend (http://localhost:3000)
- React application
- Live reload enabled (changes auto-refresh)
- All recipe content and language features

---

## Features

✅ Puerto Rican recipe database
✅ Language & vocabulary learning
✅ Quick translation tool (requires backend)
✅ Category-based recipe filtering
✅ Full-text search capability
✅ Responsive design

---

## Development Workflow

1. Make changes to React code → **Auto-reloads** (no restart needed)
2. Make changes to backend → **Requires restart** (stop and `make backend`)
3. Both services share logs in the same terminal for easy debugging

---

## Next Steps

- Explore the Language page (📖 menu)
- Check out recipe details with the translation feature
- Browse Puerto Rican recipes by category

Enjoy! 🎉
