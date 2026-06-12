@echo off
title RECONPRO - Auto Installer
color 0A
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo  ══════════════════════════════════════════
echo   RECONPRO - Windows Auto Installer
echo  ══════════════════════════════════════════
echo.

set INSTALL_DIR=%USERPROFILE%\reconpro_tools
set GOBIN=%USERPROFILE%\go\bin
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%GOBIN%" mkdir "%GOBIN%"

REM === Add paths to user PATH permanently ===
setx PATH "%PATH%;%GOBIN%;%INSTALL_DIR%" >nul 2>&1
set PATH=%PATH%;%GOBIN%;%INSTALL_DIR%

REM ==========================================
REM  1. PYTHON
REM ==========================================
echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Python not found. Downloading Python 3.12...
    echo  [-] Downloading...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe' -OutFile '%INSTALL_DIR%\python_installer.exe'" 2>nul
    if exist "%INSTALL_DIR%\python_installer.exe" (
        echo  [-] Installing Python (silent, adding to PATH)...
        "%INSTALL_DIR%\python_installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
        echo  [-] Waiting for install to finish...
        timeout /t 30 /nobreak >nul
        REM Refresh PATH
        set "PATH=%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\Scripts\"
        python --version >nul 2>&1
        if %errorlevel% equ 0 (
            echo  [OK] Python installed!
            del "%INSTALL_DIR%\python_installer.exe" >nul 2>&1
        ) else (
            echo  [!] Python installed but not in PATH yet.
            echo  [!] Close this window and open a NEW terminal, then run install.bat again.
            pause
            exit /b 1
        )
    ) else (
        echo  [!] Download failed. Install manually: https://www.python.org/downloads/
        pause
        exit /b 1
    )
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo  [OK] %%i
)

REM ==========================================
REM  2. PIP
REM ==========================================
echo.
echo [2/6] Checking pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [-] Installing pip...
    python -m ensurepip --default-pip >nul 2>&1
)
echo  [OK] pip ready

REM ==========================================
REM  3. PYTHON PACKAGES
REM ==========================================
echo.
echo [3/6] Installing Python packages...
pip install python-whois requests aiohttp --quiet --disable-pip-version-check 2>nul
if %errorlevel% equ 0 (
    echo  [OK] python-whois, requests, aiohttp
) else (
    echo  [!] Some packages failed, retrying...
    pip install python-whois requests aiohttp --disable-pip-version-check 2>nul
)

REM ==========================================
REM  4. GO
REM ==========================================
echo.
echo [4/6] Checking Go...
go version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Go not found. Downloading Go 1.22...
    echo  [-] Downloading...
    powershell -Command "Invoke-WebRequest -Uri 'https://go.dev/dl/go1.22.5.windows-amd64.msi' -OutFile '%INSTALL_DIR%\go_installer.msi'" 2>nul
    if exist "%INSTALL_DIR%\go_installer.msi" (
        echo  [-] Installing Go (silent)...
        msiexec /i "%INSTALL_DIR%\go_installer.msi" /quiet /qn
        echo  [-] Waiting for install to finish...
        timeout /t 30 /nobreak >nul
        REM Set Go paths
        set "PATH=%PATH%;C:\Program Files\Go\bin;%GOBIN%"
        setx PATH "%PATH%;C:\Program Files\Go\bin;%GOBIN%" >nul 2>&1
        go version >nul 2>&1
        if %errorlevel% equ 0 (
            echo  [OK] Go installed!
            del "%INSTALL_DIR%\go_installer.msi" >nul 2>&1
        ) else (
            echo  [!] Go installed but not in PATH yet.
            echo  [!] Close this window and open a NEW terminal, then run install.bat again.
            pause
            exit /b 1
        )
    ) else (
        echo  [!] Download failed. Install manually: https://go.dev/dl/
        pause
        exit /b 1
    )
) else (
    for /f "tokens=*" %%i in ('go version 2^>^&1') do echo  [OK] %%i
)

REM ==========================================
REM  5. GO TOOLS
REM ==========================================
echo.
echo [5/6] Installing Go tools (subfinder, httpx, naabu, dnsx)...
echo  This takes 2-5 minutes on first run.
echo.

echo  [-] subfinder...
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>nul
if %errorlevel% equ 0 (echo  [OK] subfinder) else (echo  [!] subfinder failed)

echo  [-] httpx...
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest 2>nul
if %errorlevel% equ 0 (echo  [OK] httpx) else (echo  [!] httpx failed)

echo  [-] naabu...
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest 2>nul
if %errorlevel% equ 0 (echo  [OK] naabu) else (echo  [!] naabu failed)

echo  [-] dnsx...
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest 2>nul
if %errorlevel% equ 0 (echo  [OK] dnsx) else (echo  [!] dnsx failed)

REM Copy to install dir as backup
if exist "%GOBIN%\subfinder.exe" copy "%GOBIN%\subfinder.exe" "%INSTALL_DIR%" >nul 2>&1
if exist "%GOBIN%\httpx.exe" copy "%GOBIN%\httpx.exe" "%INSTALL_DIR%" >nul 2>&1
if exist "%GOBIN%\naabu.exe" copy "%GOBIN%\naabu.exe" "%INSTALL_DIR%" >nul 2>&1
if exist "%GOBIN%\dnsx.exe" copy "%GOBIN%\dnsx.exe" "%INSTALL_DIR%" >nul 2>&1

REM ==========================================
REM  6. FINAL CHECK
REM ==========================================
echo.
echo [6/6] Final check...
echo.
set OK=0
set TOTAL=0

set /a TOTAL+=1
python --version >nul 2>&1 && (set /a OK+=1 & echo  [OK] Python) || echo  [!!] Python MISSING

set /a TOTAL+=1
go version >nul 2>&1 && (set /a OK+=1 & echo  [OK] Go) || echo  [!!] Go MISSING

set /a TOTAL+=1
where subfinder >nul 2>&1 && (set /a OK+=1 & echo  [OK] subfinder) || echo  [!!] subfinder MISSING

set /a TOTAL+=1
where httpx >nul 2>&1 && (set /a OK+=1 & echo  [OK] httpx) || echo  [!!] httpx MISSING

set /a TOTAL+=1
where naabu >nul 2>&1 && (set /a OK+=1 & echo  [OK] naabu) || echo  [!!] naabu MISSING

set /a TOTAL+=1
where dnsx >nul 2>&1 && (set /a OK+=1 & echo  [OK] dnsx) || echo  [!!] dnsx MISSING

echo.
echo  ══════════════════════════════════════════
echo   RESULT: %OK%/%TOTAL% tools ready
echo  ══════════════════════════════════════════

if %OK% geq 5 (
    echo.
    echo  Run RECONPRO now:
    echo    python "%~dp0recon.py"
    echo.
) else (
    echo.
    echo  Some tools failed. Try:
    echo  1. Close this terminal
    echo  2. Open a NEW terminal
    echo  3. Run install.bat again
    echo.
)
pause
