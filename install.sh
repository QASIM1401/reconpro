#!/bin/bash
# RECONPRO - Linux/Kali Fast Auto Installer
# Detects already-installed tools and skips them. Runs Go installs in parallel.

set -u

# Colors
GREEN='\033[1;92m'
RED='\033[1;91m'
YELLOW='\033[1;93m'
BLUE='\033[1;94m'
NC='\033[0m'

OK="${GREEN}[OK]${NC}"
FAIL="${RED}[!!]${NC}"
WARN="${YELLOW}[-]${NC}"
INFO="${BLUE}[*]${NC}"

GO_BIN="$HOME/go/bin"
mkdir -p "$GO_BIN"
export PATH="$GO_BIN:$PATH"

OK_COUNT=0
TOTAL=0
NEED_APT_UPDATE=1

# ─────────────────────────────────────────────
echo ""
echo "  ========================================"
echo "   RECONPRO Linux/Kali Fast Installer"
echo "   Skips already-installed tools"
echo "  ========================================"
echo ""

# ─── HELPERS ───
count_ok() {
    ((TOTAL++))
    [ "$1" -eq 1 ] && ((OK_COUNT++))
}

check_cmd() {
    command -v "$1" >/dev/null 2>&1
}

run_apt_update_once() {
    if [ "$NEED_APT_UPDATE" -eq 1 ]; then
        echo -e "  $INFO Updating apt package list..."
        sudo apt-get update -qq >/dev/null 2>&1
        NEED_APT_UPDATE=0
    fi
}

step() {
    echo ""
    echo -e "${BLUE}==>${NC} $1"
}

install_apt_pkg() {
    local pkg="$1"
    local cmd="${2:-$pkg}"
    if check_cmd "$cmd"; then
        echo -e "  $OK $pkg already installed"
        return 0
    fi
    run_apt_update_once
    echo -e "  $WARN Installing $pkg via apt..."
    if sudo apt-get install -y -qq "$pkg" >/dev/null 2>&1; then
        echo -e "  $OK $pkg installed"
        return 0
    else
        echo -e "  $FAIL $pkg installation failed"
        return 1
    fi
}

install_pip_pkg() {
    local pkg="$1"
    local mod="${2:-$pkg}"
    if python3 -c "import $mod" 2>/dev/null; then
        echo -e "  $OK Python package $pkg already installed"
        return 0
    fi
    echo -e "  $WARN Installing Python package $pkg..."
    if pip3 install "$pkg" --quiet --disable-pip-version-check 2>/dev/null; then
        echo -e "  $OK $pkg installed"
        return 0
    elif pip3 install "$pkg" --quiet --disable-pip-version-check --break-system-packages 2>/dev/null; then
        echo -e "  $OK $pkg installed (with --break-system-packages)"
        return 0
    else
        echo -e "  $FAIL $pkg installation failed"
        return 1
    fi
}

install_go_tool_bg() {
    local tool="$1"
    local pkg="$2"
    if check_cmd "$tool"; then
        echo -e "  $OK $tool already installed"
        return 0
    fi
    echo -e "  $WARN Installing $tool (background)..."
    (
        if go install -v "$pkg" >/dev/null 2>&1; then
            echo -e "  $OK $tool installed"
        else
            echo -e "  $FAIL $tool installation failed"
        fi
    ) &
}

# ─── PERSIST GO BIN TO PATH ───
if ! grep -qF "$HOME/go/bin" ~/.bashrc 2>/dev/null && ! grep -qF "go/bin" ~/.bashrc 2>/dev/null; then
    echo "" >> ~/.bashrc
    echo '# Added by RECONPRO installer' >> ~/.bashrc
    echo 'export PATH="$HOME/go/bin:$PATH"' >> ~/.bashrc
fi

# ─── SYSTEM DEPENDENCIES ───
step "System dependencies"
install_apt_pkg "python3" "python3" && count_ok 1 || count_ok 0
install_apt_pkg "python3-pip" "pip3" && count_ok 1 || count_ok 0
install_apt_pkg "golang-go" "go" && count_ok 1 || count_ok 0
install_apt_pkg "whois" "whois" && count_ok 1 || count_ok 0

# Ensure pip exists even if python3-pip package naming is different
if ! check_cmd "pip3"; then
    python3 -m ensurepip --default-pip >/dev/null 2>&1 || true
fi

# ─── PYTHON PACKAGES ───
step "Python packages"
install_pip_pkg "python-whois" "whois" && count_ok 1 || count_ok 0
install_pip_pkg "requests" "requests" && count_ok 1 || count_ok 0
install_pip_pkg "aiohttp" "aiohttp" && count_ok 1 || count_ok 0
install_pip_pkg "sublist3r" "sublist3r" && count_ok 1 || count_ok 0
install_pip_pkg "dnsgen" "dnsgen" && count_ok 1 || count_ok 0

# ─── GO TOOLS (parallel) ───
step "Go tools (installing in parallel)"
install_go_tool_bg "subfinder" "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
install_go_tool_bg "httpx" "github.com/projectdiscovery/httpx/cmd/httpx@latest"
install_go_tool_bg "naabu" "github.com/projectdiscovery/naabu/v2/cmd/naabu@latest"
install_go_tool_bg "dnsx" "github.com/projectdiscovery/dnsx/cmd/dnsx@latest"
install_go_tool_bg "puredns" "github.com/d3mondev/puredns/v2@latest"
install_go_tool_bg "alterx" "github.com/projectdiscovery/alterx/cmd/alterx@latest"
install_go_tool_bg "amass" "github.com/owasp-amass/amass/v4/cmd/amass@master"
wait

# Refresh shell command hash
hash -r 2>/dev/null || true

# ─── FINAL CHECK ───
step "Final verification"
OK_COUNT=0
TOTAL=0

check_cmd "python3" && echo -e "  $OK Python3" && count_ok 1 || echo -e "  $FAIL Python3"
check_cmd "go" && echo -e "  $OK Go" && count_ok 1 || echo -e "  $FAIL Go"
check_cmd "whois" && echo -e "  $OK whois" && count_ok 1 || echo -e "  $FAIL whois"

for tool in subfinder httpx naabu dnsx puredns alterx amass; do
    check_cmd "$tool" && echo -e "  $OK $tool" && count_ok 1 || echo -e "  $FAIL $tool"
done

for mod in whois requests aiohttp sublist3r dnsgen; do
    if python3 -c "import $mod" 2>/dev/null; then
        echo -e "  $OK Python module: $mod"
        count_ok 1
    else
        echo -e "  $FAIL Python module: $mod"
        count_ok 0
    fi
done

echo ""
echo "  ========================================"
echo "   Ready: $OK_COUNT/$TOTAL tools"
echo "  ========================================"
echo "  Run: python3 recon.py"
echo ""
