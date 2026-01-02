@echo off
:: Mourne - One-Click Launcher for Windows
:: Double-click this file to install dependencies and start the application

title Mourne - AI Video Director
color 0A

echo.
echo  ██████╗ ██████╗ ██╗   ██╗██████╗ ███╗   ██╗███████╗
echo  ██╔══██╗██╔══██╗██║   ██║██╔══██╗████╗  ██║██╔════╝
echo  ██████╔╝██████╔╝██║   ██║██████╔╝██╔██╗ ██║█████╗  
echo  ██╔══██╗██╔══██╗██║   ██║██╔══██╗██║╚██╗██║██╔══╝  
echo  ██████╔╝██║  ██║╚██████╔╝██║  ██║██║ ╚████║███████╗
echo  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝
echo.
echo  AI-Powered Cinematic Video Generation
echo  ========================================
echo.

:: Change to script directory
cd /d "%~dp0"

:: Check for Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Python is not installed or not in PATH!
    echo  Please install Python 3.10+ from https://python.org
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
echo       Python found!

:: Check for Node.js
echo [2/5] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Node.js is not installed or not in PATH!
    echo  Please install Node.js from https://nodejs.org
    echo.
    pause
    exit /b 1
)
echo       Node.js found!

:: Install Python dependencies
echo [3/5] Installing Python dependencies...
cd server
pip install -r requirements.txt -q
if errorlevel 1 (
    echo       Warning: Some Python dependencies may have failed to install.
) else (
    echo       Dependencies installed!
)
cd ..

:: Install Node dependencies
echo [4/5] Installing frontend dependencies...
cd client
if not exist "node_modules" (
    call npm install --silent
    echo       Frontend dependencies installed!
) else (
    echo       Frontend dependencies already installed!
)
cd ..

:: Start services
echo [5/5] Starting Mourne services...
echo.
echo  ========================================
echo  Starting backend server on port 8000...
echo  Starting frontend on port 5173...
echo  ========================================
echo.

:: Start backend in new window
start "Mourne Backend" cmd /k "cd /d "%~dp0server" && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: Wait for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend in new window
start "Mourne Frontend" cmd /k "cd /d "%~dp0client" && npm run dev"

:: Wait for frontend to start
timeout /t 5 /nobreak >nul

:: Open browser
echo.
echo  Opening browser...
start http://localhost:5173

echo.
echo  ========================================
echo  Mourne is running!
echo.
echo  Frontend:  http://localhost:5173
echo  Backend:   http://localhost:8000
echo  API Docs:  http://localhost:8000/docs
echo  ========================================
echo.
echo  Close this window to keep the servers running.
echo  To stop: Close the "Mourne Backend" and "Mourne Frontend" windows.
echo.
pause
