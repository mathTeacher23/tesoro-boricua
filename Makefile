.PHONY: help install setup start stop backend frontend dev build clean logs

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Directories
REACT_UI_DIR := react_ui
BACKEND_PORT := 8000
FRONTEND_PORT := 3000

help: ## Show this help message
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║       Tesoro Boricua - Make Commands Guide                 ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)🚀 Development Commands:$(NC)"
	@echo "  $(YELLOW)make start$(NC)       - Start both backend and frontend (best option!)"
	@echo "  $(YELLOW)make dev$(NC)         - Start in development mode with live reload"
	@echo ""
	@echo "$(GREEN)🔧 Individual Commands:$(NC)"
	@echo "  $(YELLOW)make backend$(NC)     - Start only the backend server"
	@echo "  $(YELLOW)make frontend$(NC)    - Start only the React frontend"
	@echo ""
	@echo "$(GREEN)📦 Setup & Installation:$(NC)"
	@echo "  $(YELLOW)make install$(NC)     - Install all dependencies (backend + frontend)"
	@echo "  $(YELLOW)make setup$(NC)       - Setup project (install deps + checks)"
	@echo ""
	@echo "$(GREEN)🧹 Cleanup Commands:$(NC)"
	@echo "  $(YELLOW)make stop$(NC)        - Stop all running services"
	@echo "  $(YELLOW)make clean$(NC)       - Clean build files and cache"
	@echo "  $(YELLOW)make logs$(NC)        - Show logs from running processes"
	@echo ""
	@echo "$(GREEN)📚 Production:$(NC)"
	@echo "  $(YELLOW)make build$(NC)       - Build production-ready frontend"
	@echo ""

install: ## Install all dependencies (backend + frontend)
	@echo "$(BLUE)Installing backend dependencies with uv...$(NC)"
	@command -v uv >/dev/null 2>&1 || { echo "$(RED)❌ uv not installed. Install from: https://github.com/astral-sh/uv$(NC)"; exit 1; }
	uv sync
	@echo "$(GREEN)✓ Backend dependencies installed$(NC)"
	@echo ""
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd $(REACT_UI_DIR) && npm install
	@echo "$(GREEN)✓ Frontend dependencies installed$(NC)"

setup: install ## Setup project (install deps + checks)
	@echo ""
	@echo "$(BLUE)Verifying Python version...$(NC)"
	python3 --version
	@echo ""
	@echo "$(BLUE)Verifying Node/npm version...$(NC)"
	node --version
	npm --version
	@echo ""
	@echo "$(GREEN)✓ Setup complete! Run 'make start' to launch the application$(NC)"

start: ## Start both backend and frontend
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║    🇵🇷 Starting Tesoro Boricua Application                 ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Starting backend on http://localhost:$(BACKEND_PORT)...$(NC)"
	@echo "$(YELLOW)Starting frontend on http://localhost:$(FRONTEND_PORT)...$(NC)"
	@echo ""
	@echo "$(GREEN)Press Ctrl+C to stop both services$(NC)"
	@echo ""
	@uv run python backend_server.py & \
	sleep 2 && \
	cd $(REACT_UI_DIR) && npm start
	@wait

dev: ## Start in development mode with live reload
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  🔄 Starting Tesoro Boricua in Development Mode            ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Backend:  http://localhost:$(BACKEND_PORT)$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:$(FRONTEND_PORT)$(NC)"
	@echo "$(YELLOW)API Docs: http://localhost:$(BACKEND_PORT)/docs$(NC)"
	@echo ""
	@echo "$(GREEN)Press Ctrl+C to stop both services$(NC)"
	@echo ""
	@uv run python backend_server.py & \
	BACKEND_PID=$$!; \
	sleep 2 && \
	cd $(REACT_UI_DIR) && npm start; \
	kill $$BACKEND_PID 2>/dev/null || true

backend: ## Start only the backend server
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  🚀 Starting Backend Server                                ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Server running on http://localhost:$(BACKEND_PORT)$(NC)"
	@echo "$(YELLOW)API Documentation: http://localhost:$(BACKEND_PORT)/docs$(NC)"
	@echo ""
	@echo "$(GREEN)Press Ctrl+C to stop$(NC)"
	@echo ""
	@uv run python backend_server.py

frontend: ## Start only the React frontend
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  ⚛️  Starting React Frontend                              ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Frontend running on http://localhost:$(FRONTEND_PORT)$(NC)"
	@echo ""
	@echo "$(GREEN)Press Ctrl+C to stop$(NC)"
	@echo ""
	@cd $(REACT_UI_DIR) && npm start

stop: ## Stop all running services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	@pkill -f "python3 backend_server.py" || true
	@pkill -f "react-scripts start" || true
	@pkill -f "node" || true
	@echo "$(GREEN)✓ All services stopped$(NC)"

build: ## Build production-ready frontend
	@echo "$(BLUE)Building production bundle...$(NC)"
	cd $(REACT_UI_DIR) && npm run build
	@echo "$(GREEN)✓ Build complete! Output in $(REACT_UI_DIR)/build/$(NC)"

clean: ## Clean build files and cache
	@echo "$(YELLOW)Cleaning build files...$(NC)"
	rm -rf $(REACT_UI_DIR)/build
	rm -rf $(REACT_UI_DIR)/.build-cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✓ Clean complete$(NC)"

logs: ## Show logs from running processes
	@echo "$(BLUE)Backend Server Logs:$(NC)"
	@echo "  To view backend logs, check the terminal running 'make backend'"
	@echo ""
	@echo "$(BLUE)Frontend Logs:$(NC)"
	@echo "  To view frontend logs, check the terminal running 'make frontend'"
	@echo ""
	@echo "$(BLUE)Combined View:$(NC)"
	@echo "  Run 'make start' or 'make dev' to see both logs in real-time"

# Default target
.DEFAULT_GOAL := help
