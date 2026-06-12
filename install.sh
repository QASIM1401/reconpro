#!/bin/bash
# RECONPRO - Linux/Kali Auto Installer

echo ""
echo "  ========================================"
echo "   RECONPRO Linux Installer"
echo "  ========================================"
echo ""

# Colors
GREEN='\033[1;92m'
RED='\033[1;91m'
YELLOW='\033[1;93m'
NC='\033[0m'

OK="${GREEN}[OK]${NC}"
FAIL="${RED}[!!]${NC}"
WARN="${YELLOW}[-]${NC}"

# ─── PYTHON ───
echo "[1/5] Checking Python..."
if command -v python3 &>/dev/null; then
    python3 --version
    echo -e "  $OK Python"
else
    echo -e "  $WARN Python not found, installing..."
    sudo apt install -y python3 python3-pip
fi

# ─── PIP ───
echo ""
echo "[2/5] Checking pip..."
if python3 -m pip --version &>/dev/null; then
    echo -e "  $OK pip"
else
    echo -e "  $WARN pip not found, installing..."
    sudo apt install -y python3-pip
fi

# ─── PYTHON PACKAGES ───
echo ""
echo "[3/5] Installing Python packages..."
pip3 install python-whois requests aiohttp sublist3r dnsgen --quiet 2>/dev/null
echo -e "  $OK packages"

# ─── GO TOOLS ───
echo ""
echo "[4/5] Installing Go tools (3-8 min)..."

echo "  subfinder..."
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>/dev/null

echo "  httpx..."
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest 2>/dev/null

echo "  naabu..."
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest 2>/dev/null

echo "  dnsx..."
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest 2>/dev/null

echo "  puredns..."
go install -v github.com/d3mondev/puredns/v2@latest 2>/dev/null

echo "  alterx..."
go install -v github.com/projectdiscovery/alterx/cmd/alterx@latest 2>/dev/null

# ─── CHECK ───
echo ""
echo "[5/5] Final check..."
echo ""

OK_COUNT=0

command -v python3 &>/dev/null && echo -e "  $OK Python3" && ((OK_COUNT++)) || echo -e "  $FAIL Python3"
command -v go &>/dev/null && echo -e "  $OK Go" && ((OK_COUNT++)) || echo -e "  $FAIL Go"
command -v subfinder &>/dev/null && echo -e "  $OK subfinder" && ((OK_COUNT++)) || echo -e "  $FAIL subfinder"
command -v httpx &>/dev/null && echo -e "  $OK httpx" && ((OK_COUNT++)) || echo -e "  $FAIL httpx"
command -v naabu &>/dev/null && echo -e "  $OK naabu" && ((OK_COUNT++)) || echo -e "  $FAIL naabu"
command -v dnsx &>/dev/null && echo -e "  $OK dnsx" && ((OK_COUNT++)) || echo -e "  $FAIL dnsx"
command -v puredns &>/dev/null && echo -e "  $OK puredns" && ((OK_COUNT++)) || echo -e "  $FAIL puredns"
command -v alterx &>/dev/null && echo -e "  $OK alterx" && ((OK_COUNT++)) || echo -e "  $FAIL alterx"
python3 -c "import sublist3r" 2>/dev/null && echo -e "  $OK sublist3r" && ((OK_COUNT++)) || echo -e "  $FAIL sublist3r"
python3 -c "import dnsgen" 2>/dev/null && echo -e "  $OK dnsgen" && ((OK_COUNT++)) || echo -e "  $FAIL dnsgen"

# Add Go bin to PATH if not already
GO_BIN="$HOME/go/bin"
if ! echo "$PATH" | grep -q "$GO_BIN"; then
    export PATH="$GO_BIN:$PATH"
    echo ""
    echo "  Added $GO_BIN to PATH (this session)"
    echo '  export PATH="$HOME/go/bin:$PATH"' >> ~/.bashrc
fi

echo ""
echo "  ========================================"
echo "   Ready: $OK_COUNT/10 tools"
echo "  ========================================"
echo "  Run: python3 recon.py"
echo ""
