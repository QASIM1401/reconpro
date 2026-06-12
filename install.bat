@echo off
title RECONPRO - Auto Installer
color 0A
echo.
echo  ══════════════════════════════════════════
echo   RECONPRO - Windows Auto Installer
echo  ══════════════════════════════════════════
echo.

:: Check Python
echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Python not found! Install from https://www.python.org/downloads/
    echo  [!] Make sure to check "Add Python to PATH" during install
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo  [OK] %%i

:: Check pip
echo.
echo [2/6] Checking pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] pip not found! Installing...
    python -m ensurepip --default-pip
)
echo  [OK] pip ready

:: Install Python packages
echo.
echo [3/6] Installing Python packages...
pip install python-whois requests aiohttp --quiet
if %errorlevel% neq 0 (
    echo  [!] Failed to install Python packages
) else (
    echo  [OK] python-whois, requests, aiohttp installed
)

:: Check Go
echo.
echo [4/6] Checking Go...
go version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Go not found! Install from https://go.dev/dl/
    echo  [!] Download go1.22.windows-amd64.msi and run it
    echo  [!] After install, restart this script
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('go version') do echo  [OK] %%i

:: Install Go tools
echo.
echo [5/6] Installing Go tools (subfinder, httpx, naabu, dnsx)...
echo  This may take a few minutes...

echo  [-] Installing subfinder...
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>nul
if %errorlevel% equ 0 (echo  [OK] subfinder) else (echo  [!] subfinder failed)

echo  [-] Installing httpx...
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest 2>nul
if %errorlevel% equ 0 (echo  [OK] httpx) else (echo  [!] httpx failed)

echo  [-] Installing naabu...
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest 2>nul
if %errorlevel% equ 0 (echo  [OK] naabu) else (echo  [!] naabu failed)

echo  [-] Installing dnsx...
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest 2>nul
if %errorlevel% equ 0 (echo  [OK] dnsx) else (echo  [!] dnsx failed)

:: Check Go bin
echo.
echo [6/6] Checking Go bin path...
set GOBIN=%USERPROFILE%\go\bin
if exist "%GOBIN%\subfinder.exe" (
    echo  [OK] Go bin: %GOBIN%
) else (
    echo  [!] Go bin not found at %GOBIN%
    echo  [!] Add this to your PATH: %GOBIN%
)

:: Final check
echo.
echo  ══════════════════════════════════════════
echo   INSTALLATION COMPLETE
echo  ══════════════════════════════════════════
echo.
echo  Run RECONPRO:
echo    cd %~dp0
echo    python recon.py
echo.
echo  Tools status:
python -c "import sys; print(f'  Python: {sys.version.split()[0]}')" 2>nul
go version 2>nul | python -c "import sys; print(f'  Go: {sys.stdin.read().strip()}')" 2>nul
echo  subfinder:  & where subfinder >nul 2>&1 && echo OK || echo MISSING
echo  httpx:      & where httpx >nul 2>&1 && echo OK || echo MISSING
echo  naabu:      & where naabu >nul 2>&1 && echo OK || echo MISSING
echo  dnsx:       & where dnsx >nul 2>&1 && echo OK || echo MISSING
echo.
pause
