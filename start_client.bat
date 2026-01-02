@echo off
:: Mourne - Quick Start (Frontend Only)
:: Use this if you already have the backend running

title Mourne Frontend
cd /d "%~dp0client"

echo.
echo  Starting Mourne Frontend...
echo  Will be available at: http://localhost:5173
echo.

call npm run dev
pause
