@echo off
title RECONPRO Installer
chcp 65001 >nul 2>&1

echo.
echo  ========================================
echo   RECONPRO Windows Installer
echo  ========================================
echo.

REM === CHECK PYTHON ===
python --version >nul 2>&1
if %errorlevel% equ 0 goto :PythonOK

echo  [!] Python NOT found
echo.
echo  Opening Python download page...
echo  Download Python 3.12.4 and run the installer
echo.
echo  !!! IMPORTANT !!!
echo  Check the box "Add python.exe to PATH" before clicking Install
echo.
start https://www.python.org/downloads/
echo.
echo  After installing Python, close this window.
echo  Open a NEW terminal and run install.bat again.
echo.
pause
exit /b 1

:PythonOK
python --version
echo  [OK] Python

REM === CHECK PIP ===
echo.
echo [2/5] Checking pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 python -m ensurepip --default-pip >nul 2>&1
echo  [OK] pip

REM === INSTALL PACKAGES ===
echo.
echo [3/5] Installing Python packages...
pip install python-whois requests aiohttp sublist3r dnsgen --quiet --disable-pip-version-check 2>nul
echo  [OK] packages

REM === CHECK GO ===
go version >nul 2>&1
if %errorlevel% equ 0 goto :GoOK

echo.
echo  [!] Go NOT found
echo.
echo  Opening Go download page...
echo  Download the .msi file and run it
echo.
start https://go.dev/dl/
echo.
echo  After installing Go, close this window.
echo  Open a NEW terminal and run install.bat again.
echo.
pause
exit /b 1

:GoOK
go version
echo  [OK] Go

REM === INSTALL GO TOOLS ===
echo.
echo [4/5] Installing Go tools (3-8 min)...

echo  subfinder...
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>nul
echo  httpx...
go install github.com/projectdiscovery/httpx/cmd/httpx@latest 2>nul
echo  naabu...
go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest 2>nul
echo  dnsx...
go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest 2>nul
echo  puredns...
go install github.com/d3mondev/puredns/v2@latest 2>nul
echo  alterx...
go install github.com/projectdiscovery/alterx/cmd/alterx@latest 2>nul

REM === FINAL CHECK ===
echo.
echo [5/5] Final check...
echo.

set OK=0
python --version >nul 2>&1 && (echo  [OK] Python & set /a OK=OK+1) || echo  [!!] Python
go version >nul 2>&1 && (echo  [OK] Go & set /a OK=OK+1) || echo  [!!] Go
where subfinder >nul 2>&1 && (echo  [OK] subfinder & set /a OK=OK+1) || echo  [!!] subfinder
where httpx >nul 2>&1 && (echo  [OK] httpx & set /a OK=OK+1) || echo  [!!] httpx
where naabu >nul 2>&1 && (echo  [OK] naabu & set /a OK=OK+1) || echo  [!!] naabu
where dnsx >nul 2>&1 && (echo  [OK] dnsx & set /a OK=OK+1) || echo  [!!] dnsx
where puredns >nul 2>&1 && (echo  [OK] puredns & set /a OK=OK+1) || echo  [!!] puredns
where alterx >nul 2>&1 && (echo  [OK] alterx & set /a OK=OK+1) || echo  [!!] alterx
python -c "import sublist3r" 2>nul && (echo  [OK] sublist3r & set /a OK=OK+1) || echo  [!!] sublist3r
python -c "import dnsgen" 2>nul && (echo  [OK] dnsgen & set /a OK=OK+1) || echo  [!!] dnsgen

echo.
echo  ========================================
echo   Ready: %OK%/10 tools
echo  ========================================
echo  Run: python recon.py
echo.
pause
