@echo off
title RECONPRO Installer
chcp 65001 >nul 2>&1

echo.
echo  ========================================
echo   RECONPRO Windows Installer
echo  ========================================
echo.

echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 goto :InstallPython
goto :PythonDone

:InstallPython
echo  Python not found. Trying winget...
winget --version >nul 2>&1
if %errorlevel% neq 0 goto :InstallPythonManual
echo  Installing Python via winget...
winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements --silent
goto :PythonDone

:InstallPythonManual
echo  Downloading Python installer...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe' -OutFile '%TEMP%\python_installer.exe'"
echo.
echo  ============================================
echo   IMPORTANT: Python installer will open
echo   CHECK the box that says
echo   "Add python.exe to PATH"
echo   then click Install Now
echo  ============================================
echo.
"%TEMP%\python_installer.exe"
echo.
echo  Python installed.
echo  CLOSE this terminal, open a NEW one, run install.bat again
pause
exit /b 1

:PythonDone
python --version
echo  [OK] Python ready

echo.
echo [2/6] Checking pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    python -m ensurepip --default-pip >nul 2>&1
)
echo  [OK] pip ready

echo.
echo [3/6] Installing packages...
pip install python-whois requests aiohttp --quiet --disable-pip-version-check 2>nul
echo  [OK] packages installed

echo.
echo [4/6] Checking Go...
go version >nul 2>&1
if %errorlevel% neq 0 goto :InstallGo
goto :GoDone

:InstallGo
echo  Go not found. Trying winget...
winget --version >nul 2>&1
if %errorlevel% neq 0 goto :InstallGoManual
echo  Installing Go via winget...
winget install GoLang.Go --accept-source-agreements --accept-package-agreements --silent
goto :GoDone

:InstallGoManual
echo  Downloading Go installer...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://go.dev/dl/go1.22.5.windows-amd64.msi' -OutFile '%TEMP%\go_installer.msi'"
echo  Installing Go...
msiexec /i "%TEMP%\go_installer.msi" /quiet /qn
timeout /t 40 /nobreak
goto :GoDone

:GoDone
go version
echo  [OK] Go ready

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

echo.
echo [6/6] Final check...
echo.

set OK=0

python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Python
    set /a OK=OK+1
) else (
    echo  [!!] Python MISSING
)

go version >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Go
    set /a OK=OK+1
) else (
    echo  [!!] Go MISSING
)

where subfinder >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] subfinder
    set /a OK=OK+1
) else (
    echo  [!!] subfinder MISSING
)

where httpx >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] httpx
    set /a OK=OK+1
) else (
    echo  [!!] httpx MISSING
)

where naabu >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] naabu
    set /a OK=OK+1
) else (
    echo  [!!] naabu MISSING
)

where dnsx >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] dnsx
    set /a OK=OK+1
) else (
    echo  [!!] dnsx MISSING
)

echo.
echo  ========================================
echo   Done: %OK%/6 tools ready
echo  ========================================
echo.
echo  To run: python recon.py
echo.
pause
