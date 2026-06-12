@echo off
title RECONPRO - Auto Installer
color 0A
chcp 65001 >nul 2>&1

echo.
echo  ========================================
echo   RECONPRO - Windows Auto Installer
echo  ========================================
echo.

set "INSTALL_DIR=%USERPROFILE%\reconpro_tools"
set "GOBIN=%USERPROFILE%\go\bin"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%GOBIN%" mkdir "%GOBIN%"

REM ==========================================
REM  1. PYTHON
REM ==========================================
echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Python not found. Downloading Python 3.12...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe' -OutFile '%INSTALL_DIR%\python_installer.exe'"
    if exist "%INSTALL_DIR%\python_installer.exe" (
        echo  [-] Installing Python (silent)...
        start /wait "" "%INSTALL_DIR%\python_installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
        echo  [-] Python installed. Refreshing PATH...
        set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312\;%LOCALAPPDATA%\Programs\Python\Python312\Scripts\"
        python --version >nul 2>&1
        if %errorlevel% equ 0 (
            echo  [OK] Python installed!
            del "%INSTALL_DIR%\python_installer.exe" >nul 2>&1
        ) else (
            echo  [!] Python installed. Close this window, open NEW terminal, run install.bat again.
            pause
            exit /b 1
        )
    ) else (
        echo  [!] Download failed. Install manually: https://www.python.org/downloads/
        pause
        exit /b 1
    )
) else (
    python --version 2>nul
    echo  [OK] Python found
)

REM ==========================================
REM  2. PIP
REM ==========================================
echo.
echo [2/6] Checking pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    python -m ensurepip --default-pip >nul 2>&1
)
echo  [OK] pip ready

REM ==========================================
REM  3. PYTHON PACKAGES
REM ==========================================
echo.
echo [3/6] Installing Python packages...
pip install python-whois requests aiohttp --quiet --disable-pip-version-check 2>nul
echo  [OK] python-whois, requests, aiohttp

REM ==========================================
REM  4. GO
REM ==========================================
echo.
echo [4/6] Checking Go...
go version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Go not found. Downloading Go 1.22...
    powershell -Command "Invoke-WebRequest -Uri 'https://go.dev/dl/go1.22.5.windows-amd64.msi' -OutFile '%INSTALL_DIR%\go_installer.msi'"
    if exist "%INSTALL_DIR%\go_installer.msi" (
        echo  [-] Installing Go (silent)...
        msiexec /i "%INSTALL_DIR%\go_installer.msi" /quiet /qn
        echo  [-] Waiting for install...
        timeout /t 40 /nobreak >nul
        set "PATH=%PATH%;C:\Program Files\Go\bin;%GOBIN%"
        go version >nul 2>&1
        if %errorlevel% equ 0 (
            echo  [OK] Go installed!
            del "%INSTALL_DIR%\go_installer.msi" >nul 2>&1
        ) else (
            echo  [!] Go installed. Close this window, open NEW terminal, run install.bat again.
            pause
            exit /b 1
        )
    ) else (
        echo  [!] Download failed. Install manually: https://go.dev/dl/
        pause
        exit /b 1
    )
) else (
    go version 2>nul
    echo  [OK] Go found
)

REM ==========================================
REM  5. GO TOOLS
REM ==========================================
echo.
echo [5/6] Installing Go tools (subfinder, httpx, naabu, dnsx)...
echo  This takes 2-5 minutes.
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

REM Backup tools
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
python --version >nul 2>&1
if %errorlevel% equ 0 (set /a OK+=1 & echo  [OK] Python) else (echo  [!!] Python MISSING)

set /a TOTAL+=1
go version >nul 2>&1
if %errorlevel% equ 0 (set /a OK+=1 & echo  [OK] Go) else (echo  [!!] Go MISSING)

set /a TOTAL+=1
where subfinder >nul 2>&1
if %errorlevel% equ 0 (set /a OK+=1 & echo  [OK] subfinder) else (echo  [!!] subfinder MISSING)

set /a TOTAL+=1
where httpx >nul 2>&1
if %errorlevel% equ 0 (set /a OK+=1 & echo  [OK] httpx) else (echo  [!!] httpx MISSING)

set /a TOTAL+=1
where naabu >nul 2>&1
if %errorlevel% equ 0 (set /a OK+=1 & echo  [OK] naabu) else (echo  [!!] naabu MISSING)

set /a TOTAL+=1
where dnsx >nul 2>&1
if %errorlevel% equ 0 (set /a OK+=1 & echo  [OK] dnsx) else (echo  [!!] dnsx MISSING)

echo.
echo  ========================================
echo   RESULT: %OK%/%TOTAL% tools ready
echo  ========================================
echo.
echo  Run: python recon.py
echo.
pause
