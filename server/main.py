"""
Mourne API - Media Generation Pipeline
FastAPI backend for cinematic AI video creation.
"""
import os
import uuid
import shutil
import asyncio
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from core.orchestrator import Orchestrator
from core.director import Director
from core.models import MasterPlan, VideoProject, GenerationStatus, MediaAsset, StyleReference
from core.media_backends import MediaBackendManager
from core.style_analyzer import StyleAnalyzer


# Initialize FastAPI app
app = FastAPI(
    title="Mourne API",
    description="Neural Orchestration Interface for Generative AI Video Creation",
    version="2.0"
)

# Initialize core components
orchestrator = Orchestrator(output_dir="generated_media")
director = Director()
style_analyzer = StyleAnalyzer()

# Ensure directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("generated_media", exist_ok=True)
os.makedirs("scripts", exist_ok=True)
os.makedirs("style_references", exist_ok=True)



# ============================================================================
# Request/Response Models
# ============================================================================

class CreateProjectRequest(BaseModel):
    name: str
    script: str


class CreateProjectResponse(BaseModel):
    project_id: str
    name: str
    status: str
    message: str


class GeneratePlanRequest(BaseModel):
    duration: Optional[float] = None  # Defaults to song duration if not provided


class RefinePlanRequest(BaseModel):
    feedback: str


class PlanResponse(BaseModel):
    project_name: str
    total_duration: float
    scene_count: int
    scenes: list


class GenerationStatusResponse(BaseModel):
    project_id: str
    status: str
    total_scenes: int
    completed_scenes: int
    progress_percent: float
    error: Optional[str] = None


class ScriptResponse(BaseModel):
    project_id: str
    script: str
    can_execute: bool


class ConfigRequest(BaseModel):
    # Per-model providers
    text_provider: Optional[str] = None     # 'openrouter' | 'google'
    image_provider: Optional[str] = None    # 'google' | 'replicate'
    video_provider: Optional[str] = None    # 'runway' | 'replicate' | 'google'
    
    # API Keys
    google_key: Optional[str] = None
    replicate_key: Optional[str] = None
    runway_key: Optional[str] = None
    openrouter_key: Optional[str] = None
    
    # Model names
    text_model: Optional[str] = None
    image_model: Optional[str] = None
    video_model: Optional[str] = None


class ConfigResponse(BaseModel):
    image_provider: str
    video_provider: str
    message: str


# ============================================================================
# Configuration Endpoints
# ============================================================================

@app.post("/api/config", response_model=ConfigResponse)
async def configure_provider(config: ConfigRequest):
    """
    Configure per-model providers and API keys.
    """
    try:
        # Configure media backends
        MediaBackendManager.configure(
            image_provider=config.image_provider,
            video_provider=config.video_provider,
            google_key=config.google_key,
            replicate_key=config.replicate_key,
            runway_key=config.runway_key
        )
        
        # Configure text provider (OpenRouter or Google)
        if config.openrouter_key:
            os.environ["OPENROUTER_API_KEY"] = config.openrouter_key
        if config.google_key:
            os.environ["GEMINI_API_KEY"] = config.google_key
        if config.text_model:
            os.environ["PLANNER_MODEL"] = config.text_model
            os.environ["CREATIVE_MODEL"] = config.text_model
        
        backend_config = MediaBackendManager.get_config()
        
        return ConfigResponse(
            image_provider=backend_config["image_provider"],
            video_provider=backend_config["video_provider"],
            message="Configuration updated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    backend_config = MediaBackendManager.get_config()
    return {
        **backend_config,
        "openrouter_configured": bool(os.environ.get("OPENROUTER_API_KEY"))
    }


# ============================================================================
# Project Endpoints
# ============================================================================

@app.post("/api/project/create", response_model=CreateProjectResponse)
async def create_project(
    name: str = Form(...),
    script: str = Form(...),
    audio: UploadFile = File(...)
):
    """
    Create a new video project with audio file.
    """
    try:
        # Generate unique project ID
        project_id = str(uuid.uuid4())[:8]
        
        # Save audio file
        audio_dir = os.path.join("uploads", project_id)
        os.makedirs(audio_dir, exist_ok=True)
        audio_path = os.path.join(audio_dir, audio.filename)
        
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)
        
        # Create project via orchestrator
        project = await orchestrator.create_project(
            project_id=project_id,
            name=name,
            script=script,
            song_path=audio_path
        )
        
        return CreateProjectResponse(
            project_id=project_id,
            name=name,
            status=project.status,
            message="Project created successfully. Upload complete."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/project/{project_id}")
async def get_project(project_id: str):
    """
    Get project details and current status.
    """
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "id": project.id,
        "name": project.name,
        "status": project.status,
        "has_plan": project.plan is not None,
        "asset_count": len(project.assets),
        "has_script": project.processing_script is not None,
        "has_style_reference": project.style_reference is not None
    }


@app.post("/api/project/{project_id}/style-reference")
async def upload_style_reference(project_id: str, file: UploadFile = File(...)):
    """
    Upload a reference image to analyze and extract visual style.
    The extracted style will be injected into all media generation prompts.
    """
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Save the file
    file_ext = os.path.splitext(file.filename)[1] or ".jpg"
    save_path = os.path.join("style_references", f"{project_id}_style{file_ext}")
    
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        # Analyze the image
        style_ref = await style_analyzer.analyze(save_path)
        
        # Store in project (we need to update the project object)
        # Convert to models.StyleReference
        from core.models import StyleReference as ModelStyleReference
        project.style_reference = ModelStyleReference(
            artistic_style=style_ref.artistic_style,
            rendering_technique=style_ref.rendering_technique,
            color_palette=style_ref.color_palette,
            lighting_style=style_ref.lighting_style,
            texture_quality=style_ref.texture_quality,
            mood=style_ref.mood,
            atmosphere=style_ref.atmosphere,
            composition_notes=style_ref.composition_notes,
            detail_level=style_ref.detail_level,
            style_prompt=style_ref.style_prompt,
            source_image_path=save_path
        )
        
        return {
            "message": "Style reference analyzed successfully",
            "style": {
                "artistic_style": style_ref.artistic_style,
                "rendering_technique": style_ref.rendering_technique,
                "color_palette": style_ref.color_palette,
                "lighting_style": style_ref.lighting_style,
                "mood": style_ref.mood,
                "atmosphere": style_ref.atmosphere,
                "style_prompt": style_ref.style_prompt
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Style analysis failed: {str(e)}")


@app.get("/api/project/{project_id}/style-reference")
async def get_style_reference(project_id: str):
    """
    Get the current style reference for a project.
    """
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.style_reference:
        return {"has_style": False, "style": None}
    
    return {
        "has_style": True,
        "style": project.style_reference.model_dump()
    }


# ============================================================================
# Planning Endpoints
# ============================================================================

@app.post("/api/project/{project_id}/plan", response_model=PlanResponse)
async def generate_plan(project_id: str, request: GeneratePlanRequest):
    """
    Generate a scene-by-scene plan using the Master Planner.
    """
    try:
        plan = await orchestrator.generate_plan(project_id, request.duration)
        
        return PlanResponse(
            project_name=plan.project_name,
            total_duration=plan.total_duration,
            scene_count=len(plan.scenes),
            scenes=[scene.model_dump() for scene in plan.scenes]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/project/{project_id}/plan/refine", response_model=PlanResponse)
async def refine_plan(project_id: str, request: RefinePlanRequest):
    """
    Refine the current plan based on user feedback.
    """
    try:
        plan = await orchestrator.refine_plan(project_id, request.feedback)
        
        return PlanResponse(
            project_name=plan.project_name,
            total_duration=plan.total_duration,
            scene_count=len(plan.scenes),
            scenes=[scene.model_dump() for scene in plan.scenes]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/project/{project_id}/plan")
async def get_plan(project_id: str):
    """
    Get the current plan for a project.
    """
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.plan:
        raise HTTPException(status_code=404, detail="No plan generated yet")
    
    return {
        "project_name": project.plan.project_name,
        "total_duration": project.plan.total_duration,
        "scene_count": len(project.plan.scenes),
        "scenes": [scene.model_dump() for scene in project.plan.scenes]
    }


# ============================================================================
# Media Generation Endpoints
# ============================================================================

@app.post("/api/project/{project_id}/generate")
async def start_media_generation(
    project_id: str, 
    background_tasks: BackgroundTasks
):
    """
    Start asynchronous media generation for all scenes.
    Poll /api/project/{id}/status for progress.
    """
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.plan:
        raise HTTPException(status_code=400, detail="Generate a plan first")
    
    if project.status == "generating":
        raise HTTPException(status_code=400, detail="Generation already in progress")
    
    # Start generation in background
    background_tasks.add_task(orchestrator.generate_media, project_id)
    
    return {
        "project_id": project_id,
        "status": "started",
        "message": f"Media generation started for {len(project.plan.scenes)} scenes",
        "poll_endpoint": f"/api/project/{project_id}/status"
    }


@app.get("/api/project/{project_id}/status", response_model=GenerationStatusResponse)
async def get_generation_status(project_id: str):
    """
    Get the current status of media generation.
    """
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    status = orchestrator.get_generation_status(project_id)
    
    if not status:
        return GenerationStatusResponse(
            project_id=project_id,
            status=project.status,
            total_scenes=len(project.plan.scenes) if project.plan else 0,
            completed_scenes=len(project.assets),
            progress_percent=0.0
        )
    
    return GenerationStatusResponse(
        project_id=project_id,
        status=status.status,
        total_scenes=status.total_scenes,
        completed_scenes=status.completed_scenes,
        progress_percent=status.progress_percent,
        error=status.error
    )


@app.get("/api/project/{project_id}/assets")
async def get_assets(project_id: str):
    """
    Get all generated assets for a project.
    """
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "project_id": project_id,
        "asset_count": len(project.assets),
        "assets": [
            {
                "path": asset.asset_path,
                "type": asset.media_type.value,
                "scene_number": asset.stitching_card.scene_number,
                "time_start": asset.stitching_card.time_start,
                "time_end": asset.stitching_card.time_end,
                "prompt": asset.stitching_card.visual_prompt[:200] + "..."
            }
            for asset in project.assets
        ]
    }


# ============================================================================
# Director / Script Endpoints
# ============================================================================

@app.get("/api/project/{project_id}/script", response_model=ScriptResponse)
async def get_processing_script(project_id: str, use_llm: bool = False):
    """
    Get the generated MoviePy processing script.
    
    Args:
        use_llm: If True, use LLM to generate script. If False, use deterministic generator.
    """
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.assets:
        raise HTTPException(status_code=400, detail="No assets generated yet")
    
    try:
        if use_llm:
            script = await director.generate_processing_script(project)
        else:
            script = director.generate_static_script(project)
        
        return ScriptResponse(
            project_id=project_id,
            script=script,
            can_execute=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/project/{project_id}/script/save")
async def save_script(project_id: str):
    """
    Save the processing script to a file for user review/execution.
    """
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Generate script if not exists
    if not project.processing_script:
        project.processing_script = director.generate_static_script(project)
    
    # Save to file
    script_path = os.path.join("scripts", f"render_{project_id}.py")
    with open(script_path, 'w') as f:
        f.write(project.processing_script)
    
    return {
        "project_id": project_id,
        "script_path": script_path,
        "message": f"Script saved. Run with: python {script_path}"
    }


@app.post("/api/project/{project_id}/execute")
async def execute_script(project_id: str, background_tasks: BackgroundTasks):
    """
    Execute the processing script to render the final video.
    Note: This runs in background and may take several minutes.
    """
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    script_path = os.path.join("scripts", f"render_{project_id}.py")
    
    if not os.path.exists(script_path):
        # Generate and save script first
        if not project.processing_script:
            project.processing_script = director.generate_static_script(project)
        
        with open(script_path, 'w') as f:
            f.write(project.processing_script)
    
    # Execute in background
    async def run_script():
        import subprocess
        project.status = "rendering"
        try:
            result = subprocess.run(
                ["python", script_path],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            if result.returncode == 0:
                project.status = "complete"
            else:
                project.status = "failed"
                print(f"Render error: {result.stderr}")
        except Exception as e:
            project.status = "failed"
            print(f"Execution error: {e}")
    
    background_tasks.add_task(run_script)
    
    return {
        "project_id": project_id,
        "status": "rendering",
        "message": "Video rendering started. This may take several minutes.",
        "output_path": f"final_{project_id}.mp4"
    }


# ============================================================================
# Utility Endpoints
# ============================================================================

@app.post("/api/upload/audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload an audio file for a project.
    """
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", file.filename)
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    return {"path": file_path, "filename": file.filename}


# Store for custom assets (in production, use a database)
_custom_assets: dict = {}


@app.post("/api/project/{project_id}/asset/upload")
async def upload_custom_asset(
    project_id: str,
    file: UploadFile = File(...)
):
    """
    Upload a custom image asset for a project.
    Users can upload their own images instead of using AI generation.
    """
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create assets directory
    asset_dir = os.path.join("uploads", project_id, "custom_assets")
    os.makedirs(asset_dir, exist_ok=True)
    
    # Generate unique asset ID
    asset_id = str(uuid.uuid4())[:8]
    file_ext = os.path.splitext(file.filename)[1] or ".png"
    file_path = os.path.join(asset_dir, f"{asset_id}{file_ext}")
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Store in memory (would be DB in production)
    if project_id not in _custom_assets:
        _custom_assets[project_id] = {}
    
    _custom_assets[project_id][asset_id] = {
        "id": asset_id,
        "path": file_path,
        "name": file.filename,
        "bound_scene": None
    }
    
    return {
        "asset_id": asset_id,
        "path": file_path,
        "name": file.filename,
        "message": "Asset uploaded successfully"
    }


@app.post("/api/project/{project_id}/asset/bind")
async def bind_asset_to_scene(
    project_id: str,
    asset_id: str,
    scene_number: int
):
    """
    Bind a custom asset to a specific scene.
    This tells the pipeline to use this image instead of generating one.
    """
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project_id not in _custom_assets or asset_id not in _custom_assets[project_id]:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Update binding
    _custom_assets[project_id][asset_id]["bound_scene"] = scene_number
    
    return {
        "asset_id": asset_id,
        "bound_scene": scene_number,
        "message": f"Asset bound to scene {scene_number}"
    }


@app.get("/api/project/{project_id}/assets/custom")
async def get_custom_assets(project_id: str):
    """
    Get all custom assets for a project.
    """
    if project_id not in _custom_assets:
        return {"assets": []}
    
    return {"assets": list(_custom_assets[project_id].values())}


@app.delete("/api/project/{project_id}/asset/{asset_id}")
async def delete_custom_asset(project_id: str, asset_id: str):
    """
    Delete a custom asset.
    """
    if project_id not in _custom_assets or asset_id not in _custom_assets[project_id]:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    asset = _custom_assets[project_id].pop(asset_id)
    
    # Delete file
    if os.path.exists(asset["path"]):
        os.remove(asset["path"])
    
    return {"deleted": asset_id}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0",
        "components": {
            "orchestrator": "ready",
            "director": "ready"
        }
    }


# Mount static files for generated media
app.mount("/media", StaticFiles(directory="generated_media"), name="media")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
