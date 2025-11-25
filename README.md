# 🇵🇷 START HERE - Tesoro Boricua

Welcome! This is the easiest way to launch the entire application.

---

## 🚀 Quick Start (Just Copy & Paste!)

### macOS/Linux Users:
```bash
cd /path/to/TESORO_BORICUA
make start
```

### Windows Users:
```bash
cd path\to\TESORO_BORICUA
start.bat
```

That's it! Both the backend server and React app will launch automatically.

---

## ✅ What Happens After Running `make start`

1. ✅ Backend server starts on http://localhost:8000
2. ✅ React frontend starts on http://localhost:3000
3. ✅ Your browser opens to the app
4. ✅ Both services run in the same terminal
5. ✅ Live reload enabled (changes auto-refresh)

---

## 🎯 Next Steps After Launch

1. **Home Page**: Explore the main features
2. **Recipes Page**: Browse Puerto Rican recipes
3. **Language Page**: Learn words and use Quick Translation
4. **Try Translation**: Opens on the right side (if backend is running)

---

## 🛑 Stopping Everything

Press **`Ctrl+C`** in the terminal to stop both services gracefully.

---

## 🆘 Something Not Working?

### If translation shows "Failed to fetch":
- Make sure you used `make start` (not just individual commands)
- Check that backend is running: http://localhost:8000/api/health
- You should see a "healthy" response

### If ports are already in use:
Run this to stop any existing processes:
```bash
make stop
```

### If you need more help:
- Check `README_STARTUP.md` for detailed troubleshooting
- Check `QUICKSTART.md` for all available commands

---

## 📚 All Available Commands

```bash
make start      # ⭐ START BOTH (recommended!)
make backend    # Backend only
make frontend   # Frontend only
make install    # Install dependencies (first time only)
make stop       # Stop all services
make help       # Show all commands
make build      # Build for production
make clean      # Clean build files
```

---

## 🔗 Important Links (When Running)

- **Main App**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

---

## 📋 First Time Setup Checklist

- [ ] Installed Python 3.7+ (check: `python3 --version`)
- [ ] Installed Node.js 14+ (check: `node --version`)
- [ ] Run `make install` (or included start.sh / start.bat)
- [ ] Run `make start` to launch

---

## 💡 Pro Tips

1. **React Changes Auto-Reload**: Just edit and save, the browser refreshes automatically
2. **Backend Changes Need Restart**: Press `Ctrl+C` and run `make start` again
3. **Can't Stop?**: Press `Ctrl+C` twice if it doesn't respond
4. **View Logs**: Both services log to the same terminal for easy debugging

---

## 🎉 That's All!

You're ready to go! Run `make start` and start exploring.

For more details, see:
- `QUICKSTART.md` - Quick reference of all commands
- `README_STARTUP.md` - Detailed setup and troubleshooting
- `Makefile` - Source of all automation commands

Enjoy Tesoro Boricua! 🇵🇷
