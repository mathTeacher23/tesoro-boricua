#!/bin/bash
# Tesoro Boricua - Universal Start Script
# Works on macOS, Linux, and Windows (Git Bash)

set -e

# Color codes
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    🇵🇷 Tesoro Boricua - Launching Application              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if Make is available
if command -v make &> /dev/null; then
    echo -e "${GREEN}✓ Make found! Using make start...${NC}"
    make start
else
    echo -e "${YELLOW}⚠️  Make not found. Starting services manually...${NC}"
    echo ""

    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is not installed!${NC}"
        exit 1
    fi

    # Check Node
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js is not installed!${NC}"
        exit 1
    fi

    echo -e "${YELLOW}Starting backend server...${NC}"
    python3 backend_server.py &
    BACKEND_PID=$!

    sleep 2

    echo -e "${YELLOW}Starting React frontend...${NC}"
    cd react_ui
    npm start

    # Cleanup
    trap "kill $BACKEND_PID 2>/dev/null || true" EXIT
fi
