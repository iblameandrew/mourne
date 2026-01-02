# Mourne - The Obsidian Siren

Mourne is a Generative AI Video Creation Engine. It orchestrates AI models to turn text scripts and music into cinematic music videos.

## Directory Structure
- `client/`: React + Vite Frontend (The "Obsidian Siren" UI).
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
