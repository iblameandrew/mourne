# Mourne
<div align="center">
  <img src="client/public/logo_v2.png" width="150" alt="Mourne Logo" />
</div>

Mourne is a comprehensive Neural Orchestration Interface for Generative AI Video Creation. It orchestrates local and cloud-based AI models to turn text scripts and music into cinematic experiences.

## Quick Start (Windows)

**One-Click Launch:** Double-click `START_MOURNE.bat` to automatically:
- Check for Python and Node.js
- Install all dependencies
- Start the backend and frontend servers
- Open the app in your browser

> **Prerequisites:** [Python 3.10+](https://python.org) and [Node.js](https://nodejs.org) must be installed.

## Directory Structure
- `client/`: React + Vite Frontend (The Spectral Terminal UI).
- `server/`: FastAPI Backend (Orchestrator, Director, AI Logic).

## Manual Setup

### Backend
```bash
cd server
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd client
npm install
npm run dev
```

## API Documentation
Once running, visit http://localhost:8000/docs for the interactive API docs.

## License
MIT
