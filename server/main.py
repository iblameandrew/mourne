from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
import shutil
import os
from core.orchestrator import Orchestrator
from core.director import Director, VideoProject, StitchingCard

app = FastAPI(title="Mourne API", version="1.0")

# Setup Logic
orchestrator = Orchestrator()
director = Director()

# Models
class AnalysisRequest(BaseModel):
    script: str
    
class PlanResponse(BaseModel):
    analysis: str

# Endpoints
@app.post("/api/analyze", response_model=PlanResponse)
async def analyze_script(request: AnalysisRequest):
    """
    Analyzes the script and returns a high-level plan.
    """
    try:
        result = await orchestrator.run_analysis(request.script)
        return PlanResponse(analysis=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Uploads an audio file/score.
    """
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"path": file_path, "filename": file.filename}

# Static Files (for assets and eventually the React build)
# app.mount("/", StaticFiles(directory="../client/dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
