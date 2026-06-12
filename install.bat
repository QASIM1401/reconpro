@echo off
title RECONPRO Installer
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo  ========================================
echo   RECONPRO Windows Installer
echo  ========================================
echo.

REM === PYTHON ===
echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Python not found

    REM Try winget first
    winget --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo  [-] Installing Python via winget...
        winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements --silent
        if %errorlevel% equ 0 (
            echo  [OK] Python installed via winget
        )
    ) else (
        REM Download and install manually
        echo  [-] winget not available, downloading Python...
        powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe' -OutFile '%TEMP%\python_installer.exe'"
        if exist "%TEMP%\python_installer.exe" (
            echo  [-] Running Python installer (please follow the wizard)...
            "%TEMP%\python_installer.exe"
            echo  [-] After install, CLOSE this window and open a NEW terminal
            echo  [-] Then run install.bat again
            pause
            exit /b 1
        ) else (
            echo  [!] Download failed
            echo  [!] Download manually: https://www.python.org/downloads/
            echo  [!] IMPORTANT: Check "Add Python to PATH" during install
            pause
            exit /b 1
        )
    )

    REM Refresh PATH for this session
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312\;%LOCALAPPDATA%\Programs\Python\Python312\Scripts\"
    set "PATH=%PATH%;C:\Python312\;C:\Python312\Scripts\"

    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [!] Python not in PATH yet
        echo  [!] CLOSE this window, open NEW terminal, run install.bat again
        pause
        exit /b 1
    )
)
python --version
echo  [OK] Python ready

REM === PIP ===
echo.
echo [2/6] Checking pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    python -m ensurepip --default-pip >nul 2>&1
)
echo  [OK] pip ready

REM === PACKAGES ===
echo.
echo [3/6] Installing packages...
pip install python-whois requests aiohttp --quiet --disable-pip-version-check 2>nul
echo  [OK] packages installed

REM === GO ===
echo.
echo [4/6] Checking Go...
go version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Go not found

    REM Try winget first
    winget --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo  [-] Installing Go via winget...
        winget install GoLang.Go --accept-source-agreements --accept-package-agreements --silent
        if %errorlevel% equ 0 (
            echo  [OK] Go installed via winget
        )
    ) else (
        echo  [-] Downloading Go...
        powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://go.dev/dl/go1.22.5.windows-amd64.msi' -OutFile '%TEMP%\go_installer.msi'"
        if exist "%TEMP%\go_installer.msi" (
            echo  [-] Installing Go...
            msiexec /i "%TEMP%\go_installer.msi" /quiet /qn
            timeout /t 40 /nobreak
        ) else (
            echo  [!] Download failed
            echo  [!] Download manually: https://go.dev/dl/
            pause
            exit /b 1
        )
    )

    set "PATH=%PATH%;C:\Program Files\Go\bin;%USERPROFILE%\go\bin"

    go version >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [!] Go not in PATH yet
        echo  [!] CLOSE this window, open NEW terminal, run install.bat again
        pause
        exit /b 1
    )
)
go version
echo  [OK] Go ready

REM === GO TOOLS ===
echo.
echo [5/6] Installing Go tools (2-5 min)...
echo.

echo  [-] subfinder...
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>nul
if %errorlevel% equ 0 (echo  [OK] subfinder) else (echo  [!] subfinder failed)

echo  [-] httpx...
go install github.com/projectdiscovery/httpx/cmd/httpx@latest 2>nul
if %errorlevel% equ 0 (echo  [OK] httpx) else (echo  [!] httpx failed)

echo  [-] naabu...
go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest 2>nul
if %errorlevel% equ 0 (echo  [OK] naabu) else (echo  [!] naabu failed)

echo  [-] dnsx...
go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest 2>nul
if %errorlevel% equ 0 (echo  [OK] dnsx) else (echo  [!] dnsx failed)

REM === FINAL CHECK ===
echo.
echo [6/6] Final check...
echo.

set OK=0

python --version >nul 2>&1 && (echo  [OK] Python & set /a OK+=1) || echo  [!!] Python MISSING
go version >nul 2>&1 && (echo  [OK] Go & set /a OK+=1) || echo  [!!] Go MISSING
where subfinder >nul 2>&1 && (echo  [OK] subfinder & set /a OK+=1) || echo  [!!] subfinder MISSING
where httpx >nul 2>&1 && (echo  [OK] httpx & set /a OK+=1) || echo  [!!] httpx MISSING
where naabu >nul 2>&1 && (echo  [OK] naabu & set /a OK+=1) || echo  [!!] naabu MISSING
where dnsx >nul 2>&1 && (echo  [OK] dnsx & set /a OK+=1) || echo  [!!] dnsx MISSING

echo.
echo  ========================================
echo   Done: %OK%/6 tools ready
echo  ========================================
echo.

if %OK% lss 6 (
    echo  Some tools missing.
    echo  CLOSE this terminal, open NEW one, run install.bat again
    echo.
)

echo  To run: python recon.py
echo.
pause
