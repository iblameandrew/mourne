@echo off
:: Mourne - Quick Start (Server Only)
:: Use this if you only need the backend API

title Mourne API Server
cd /d "%~dp0server"

echo.
echo  Starting Mourne API Server...
echo  API will be available at: http://localhost:8000
echo  API Documentation: http://localhost:8000/docs
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
