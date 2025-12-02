.PHONY: install dev run backend frontend help

help:
	@echo "TESORO Boricua Validation App"
	@echo ""
	@echo "Available commands:"
	@echo "  make install   - Install dependencies with uv"
	@echo "  make dev       - Install dependencies and run both backend and frontend"
	@echo "  make backend   - Run Flask backend only"

install:
	@echo "Installing dependencies with uv..."
	uv sync

dev: install
	@echo "Starting TESORO Validation App..."
	@echo "Backend will run on http://localhost:5001"
	@echo "Frontend will run on http://localhost:8000"
	@echo "Open http://localhost:8000 in your browser"
	@echo ""
	uv run python app.py &
	sleep 2
	python -m http.server 8000 --directory .

backend: install
	@echo "Starting Flask backend..."
	uv run python app.py
