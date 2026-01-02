# Contributing to Mourne

Thank you for your interest in contributing to the **Mourne** project!

## Architecture
Mourne is a web-based generative video engine.
- **Frontend**: React (Vite) + TailwindCSS. Located in `client/`.
- **Backend**: FastAPI (Python). Located in `server/`.

## Getting Started

1. **Fork and Clone** the repository.
2. **Install Backend Dependencies**:
   ```bash
   cd server
   pip install -r requirements.txt
   ```
3. **Install Frontend Dependencies**:
   ```bash
   cd client
   npm install
   ```

## Workflow
1. Create a branch for your feature: `git checkout -b feature/amazing-feature`.
2. Commit your changes: `git commit -m 'Add some amazing feature'`.
3. Push to the branch: `git push origin feature/amazing-feature`.
4. Open a Pull Request.

## Code Style
- **Python**: Follow PEP 8.
- **JavaScript/React**: Use functional components and hooks. Prettier recommended.
