@echo off
title RECONPRO Installer
chcp 65001 >nul 2>&1

echo.
echo  ========================================
echo   RECONPRO Windows Installer
echo  ========================================
echo.

REM === PYTHON ===
echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Python not found! Downloading...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe' -OutFile '%TEMP%\python_setup.exe'"
    echo  Installing Python silently...
    "%TEMP%\python_setup.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    timeout /t 30 /nobreak
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312\;%LOCALAPPDATA%\Programs\Python\Python312\Scripts\"
    echo  Python installed
) else (
    echo  Python found
)

REM === PIP ===
echo.
echo [2/6] Checking pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    python -m ensurepip --default-pip >nul 2>&1
)
echo  pip ready

REM === PACKAGES ===
echo.
echo [3/6] Installing packages...
pip install python-whois requests aiohttp --quiet --disable-pip-version-check 2>nul
echo  packages installed

REM === GO ===
echo.
echo [4/6] Checking Go...
go version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Go not found! Downloading...
    powershell -Command "Invoke-WebRequest -Uri 'https://go.dev/dl/go1.22.5.windows-amd64.msi' -OutFile '%TEMP%\go_setup.msi'"
    echo  Installing Go silently...
    msiexec /i "%TEMP%\go_setup.msi" /quiet /qn
    timeout /t 40 /nobreak
    set "PATH=%PATH%;C:\Program Files\Go\bin;%USERPROFILE%\go\bin"
    echo  Go installed
) else (
    echo  Go found
)

REM === GO TOOLS ===
echo.
echo [5/6] Installing Go tools...
echo  (subfinder, httpx, naabu, dnsx - takes 2-5 min)
echo.

echo  subfinder...
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>nul
echo  httpx...
go install github.com/projectdiscovery/httpx/cmd/httpx@latest 2>nul
echo  naabu...
go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest 2>nul
echo  dnsx...
go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest 2>nul
echo  Go tools done

REM === CHECK ===
echo.
echo [6/6] Checking tools...
echo.

set FOUND=0

python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Python
    set /a FOUND+=1
) else (
    echo  [!!] Python
)

go version >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Go
    set /a FOUND+=1
) else (
    echo  [!!] Go
)

where subfinder >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] subfinder
    set /a FOUND+=1
) else (
    echo  [!!] subfinder
)

where httpx >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] httpx
    set /a FOUND+=1
) else (
    echo  [!!] httpx
)

where naabu >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] naabu
    set /a FOUND+=1
) else (
    echo  [!!] naabu
)

where dnsx >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] dnsx
    set /a FOUND+=1
) else (
    echo  [!!] dnsx
)

echo.
echo  ========================================
echo   Done: %FOUND%/6 tools ready
echo  ========================================
echo.
echo  Run: python recon.py
echo.
pause
