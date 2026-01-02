# Mourne
<div align="center">
  <img src="client/public/logo_v2.png" width="150" alt="Mourne Logo" />
</div>

Mourne is a comprehensive Neural Orchestration Interface for Generative AI Video Creation. It orchestrates local and cloud-based AI models to turn text scripts and music into cinematic experiences.

## Directory Structure
- `client/`: React + Vite Frontend (The Spectral Terminal UI).
- `server/`: FastAPI Backend (Orchestrator, Director, AI Logic).
- `legacy_desktop/`: (Archived) Original PyQt6 desktop prototype.

## Running the Application

### 1. Backend
```bash
cd server
pip install -r requirements.txt
python main.py
```

### 2. Frontend
```bash
cd client
npm install
npm run dev
```

## License
MIT
