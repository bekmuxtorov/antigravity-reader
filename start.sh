#!/usr/bin/env bash
# ==============================================================================
# Antigravity Reader — Startup Script
# Fast launcher with port checking and CLI parameter forwarding.
# ==============================================================================

set -e

# Resolve script directory even if symlinked
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
PROJECT_DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
cd "$PROJECT_DIR"

# ANSI styling
BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check python3
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}❌ Xatolik: python3 tizimda topilmadi. Iltimos, Python 3.8+ o'rnating.${NC}"
    exit 1
fi

DEFAULT_PORT="${PORT:-5050}"

# Auto clean conflicting processes on port
OLD_PID=$(lsof -ti :"$DEFAULT_PORT" 2>/dev/null || fuser "$DEFAULT_PORT"/tcp 2>/dev/null || true)
if [ -n "$OLD_PID" ]; then
    echo -e "${YELLOW}⚠️  Port $DEFAULT_PORT da eski jarayon (PID: $OLD_PID) aniqlandi. Tozalanmoqda...${NC}"
    kill -9 $OLD_PID 2>/dev/null || true
    sleep 0.5
fi

echo -e "${CYAN}================================================================${NC}"
echo -e "${BOLD}${GREEN}  🚀 Antigravity Reader ishga tushirilmoqda...${NC}"
echo -e "  🌐 Veb sahifa: ${CYAN}http://localhost:${DEFAULT_PORT}${NC}"
echo -e "  📁 Katalog:    ${PROJECT_DIR}"
echo -e "  ⚡ To'xtatish: Ctrl + C"
echo -e "${CYAN}================================================================${NC}"

# Execute with arguments forwarded
exec python3 server.py "$@"
