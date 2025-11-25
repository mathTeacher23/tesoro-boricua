# 🚀 Tesoro Boricua - Application Startup Guide

This guide explains how to start both the backend server and React frontend with minimal effort.

---

## ⚡ Quick Start (Recommended)

### Option 1: Using Make (macOS/Linux)
```bash
cd /path/to/TESORO_BORICUA
make start
```

### Option 2: Using Shell Script (macOS/Linux/Git Bash)
```bash
cd /path/to/TESORO_BORICUA
./start.sh
```

### Option 3: Using Batch File (Windows)
```bash
cd path\to\TESORO_BORICUA
start.bat
```

All three options will start both services automatically!

---

## 🛠️ All Available Make Commands

### Getting Started
```bash
make install    # Install dependencies (one-time setup)
make setup      # Full setup with checks
make help       # Show all commands with descriptions
```

### Starting Services
```bash
make start      # ⭐ START BOTH BACKEND + FRONTEND (recommended!)
make dev        # Start with live reload enabled
make backend    # Start ONLY backend server
make frontend   # Start ONLY React frontend
```

### Maintenance
```bash
make stop       # Stop all running services
make clean      # Clean build files and cache
make build      # Build for production
make logs       # View log information
```

---

## 📊 What Gets Launched

### Backend Server
- **Address**: http://localhost:8000
- **Endpoints**:
  - Translation: `POST /api/translate`
  - Health Check: `GET /api/health`
  - API Docs: `GET /docs` (Swagger UI)
- **Technology**: FastAPI + Uvicorn

### Frontend Application
- **Address**: http://localhost:3000
- **Technology**: React with live reload
- **Port Forwarding**: Uses localhost:8000 for API calls

---

## 🔧 Manual Setup (If Make Not Available)

### 1. Install Backend Dependencies
```bash
pip install fastapi uvicorn translate
```

### 2. Install Frontend Dependencies
```bash
cd react_ui
npm install
cd ..
```

### 3. Start Backend
```bash
python3 backend_server.py
```

### 4. Start Frontend (in a new terminal)
```bash
cd react_ui
npm start
```

---

## ✅ Verification Checklist

After running `make start`, verify everything works:

- [ ] Backend running at http://localhost:8000
- [ ] Frontend running at http://localhost:3000
- [ ] Browser opens to React app automatically
- [ ] API docs available at http://localhost:8000/docs
- [ ] Health check works: curl http://localhost:8000/api/health

---

## 🐛 Troubleshooting

### "Failed to fetch" on Translation Feature
**Problem**: The Quick Translation tool shows "Failed to fetch"
**Solution**:
- Ensure you used `make start` (not just `make frontend`)
- Check backend is running on localhost:8000
- Try the health check: http://localhost:8000/api/health

### Port Already in Use
**Problem**: "Address already in use" for port 3000 or 8000
**Solution**:
1. Find what's using the port:
   ```bash
   # macOS/Linux
   lsof -i :3000
   lsof -i :8000

   # Windows
   netstat -ano | findstr :3000
   netstat -ano | findstr :8000
   ```
2. Kill the process or use `make stop`
3. Try again

### Make Command Not Found (Windows)
**Problem**: Windows doesn't recognize `make` command
**Solution**:
- Use `start.bat` instead: `start.bat`
- Or install Make from: http://gnuwin32.sourceforge.net/packages/make.htm

### Dependencies Not Installing
**Problem**: `pip install` or `npm install` fails
**Solution**:
```bash
# Update pip
python -m pip install --upgrade pip

# Try installing again
pip install fastapi uvicorn translate

# For npm
npm install
```

### Module Import Error (Python)
**Problem**: "No module named 'fastapi'" when running backend
**Solution**:
```bash
pip install --upgrade fastapi uvicorn translate
```

---

## 📁 Project Structure

```
TESORO_BORICUA/
├── Makefile                    # All automation commands ⭐ USE THIS
├── start.sh                    # Shell script (macOS/Linux)
├── start.bat                   # Batch file (Windows)
├── QUICKSTART.md               # Quick reference guide
├── .env.example                # Environment variables template
│
├── backend_server.py           # FastAPI server
├── main.py                     # (legacy/other script)
│
├── react_ui/                   # React Frontend
│   ├── package.json
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── ...
│   └── public/
│
└── data/                       # Data files
    └── ...
```

---

## 🎯 Common Workflows

### First Time Setup
```bash
cd /path/to/TESORO_BORICUA
make install      # Install dependencies
make setup        # Verify everything
make start        # Launch the app!
```

### Daily Development
```bash
make start        # Just start both services
# ... make changes to code ...
# Frontend auto-reloads on save
# For backend changes: Ctrl+C, then make start again
```

### Stopping Everything
```bash
make stop         # Stop all services gracefully
```

### Production Build
```bash
make build        # Creates optimized bundle in react_ui/build
```

---

## 🔐 Environment Variables

Copy `.env.example` to `.env` to customize settings:
```bash
cp .env.example .env
# Edit .env with your preferences
```

Key variables:
```
BACKEND_PORT=8000           # Backend server port
FRONTEND_PORT=3000          # React frontend port
API_BASE_URL=http://localhost:8000  # API endpoint
```

---

## 📚 Additional Resources

- **FastAPI Docs**: http://localhost:8000/docs (when running)
- **React Documentation**: https://react.dev
- **React Router**: https://reactrouter.com/
- **CORS Issues**: See backend_server.py for allowed origins

---

## 🤝 Contributing

When making changes:
1. Frontend changes auto-reload (no restart needed)
2. Backend changes require restart: `Ctrl+C` then `make start`
3. Dependencies changed? Run `make install` again
4. Build issues? Try `make clean` then reinstall

---

## 📝 Notes

- Both services run in the same terminal (easier to see all logs)
- Press `Ctrl+C` once to stop both services gracefully
- The React app is served on port 3000 with hot reload enabled
- Backend API is on port 8000 with auto-reload enabled
- All communication is over localhost (local network only)

---

## ✨ That's It!

You're now ready to develop and run Tesoro Boricua. Enjoy! 🇵🇷

Have questions? Check QUICKSTART.md for more details.
