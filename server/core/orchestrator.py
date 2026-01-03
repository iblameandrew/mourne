"""
Main Orchestrator for Mourne.
Coordinates the full media generation pipeline:
Master Planner → Sub-Agents → Final Director
"""
import os
import asyncio
from typing import Optional, Dict, Any, Callable
from .models import (
    VideoProject,
    MasterPlan,
    MediaAsset,
    GenerationStatus
)
from .master_planner import MasterPlanner
from .sub_agents import MediaGenerationCoordinator
from .llm_backend import OpenRouterLLM

# Audio duration extraction
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


class Orchestrator:
    """
    Main orchestrator for the Mourne media generation pipeline.
    
    Flow:
    1. Analyze audio (transcription/beat detection)
    2. Run Master Planner to create scene breakdown
    3. Dispatch sub-agents to generate media for each scene
    4. Collect all assets with stitching cards
    5. Pass to Director for final script generation
    """
    
    def __init__(
        self,
        output_dir: str = "generated_media",
        planner: Optional[MasterPlanner] = None,
        coordinator: Optional[MediaGenerationCoordinator] = None
    ):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.planner = planner or MasterPlanner()
        self.coordinator = coordinator or MediaGenerationCoordinator(output_dir)
        
        # Track active projects
        self._projects: Dict[str, VideoProject] = {}
        self._generation_status: Dict[str, GenerationStatus] = {}
    
    async def analyze_audio(self, audio_path: str) -> str:
        """
        Analyze audio file for lyrics/content.
        Uses Whisper via a cloud service or returns placeholder.
        
        Args:
            audio_path: Path to the audio file
        
        Returns:
            Transcription or audio analysis text
        """
        # For now, use a simple LLM-based description if no transcription service
        # In production, integrate with Whisper API or similar
        
        if not os.path.exists(audio_path):
            return "No audio file provided - instrumental track assumed"
        
        # TODO: Integrate with cloud transcription service
        # For now, return a placeholder that can be enhanced
        return f"Audio track from: {os.path.basename(audio_path)}"
    
    def extract_audio_duration(self, audio_path: str) -> float:
        """
        Extract the duration of an audio file in seconds.
        
        Args:
            audio_path: Path to the audio file
        
        Returns:
            Duration in seconds, or 60.0 as fallback
        """
        if not os.path.exists(audio_path):
            print(f"Warning: Audio file not found: {audio_path}")
            return 60.0  # Default fallback
        
        if PYDUB_AVAILABLE:
            try:
                audio = AudioSegment.from_file(audio_path)
                duration = len(audio) / 1000.0  # Convert ms to seconds
                print(f"Extracted audio duration: {duration:.2f}s")
                return duration
            except Exception as e:
                print(f"Warning: Failed to extract audio duration: {e}")
                return 60.0
        else:
            print("Warning: pydub not available, using default duration")
            return 60.0
    
    async def create_project(
        self,
        project_id: str,
        name: str,
        script: str,
        song_path: str
    ) -> VideoProject:
        """
        Initialize a new video project.
        
        Args:
            project_id: Unique project identifier
            name: Human-readable project name
            script: Creative script/concept
            song_path: Path to audio file
        
        Returns:
            Created VideoProject
        """
        # Analyze the audio
        audio_analysis = await self.analyze_audio(song_path)
        
        # Extract song duration
        song_duration = self.extract_audio_duration(song_path)
        
        project = VideoProject(
            id=project_id,
            name=name,
            script=script,
            song_path=song_path,
            song_duration=song_duration,
            audio_analysis=audio_analysis,
            status="created"
        )
        
        self._projects[project_id] = project
        return project
    
    async def generate_plan(
        self,
        project_id: str,
        duration: float = None
    ) -> MasterPlan:
        """
        Generate a scene-by-scene plan for a project.
        
        Args:
            project_id: The project to plan
            duration: Total video duration in seconds (defaults to song duration)
        
        Returns:
            Generated MasterPlan
        """
        project = self._projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Use song duration if no explicit duration provided
        if duration is None or duration <= 0:
            if project.song_duration:
                duration = project.song_duration
                print(f"Using song duration: {duration:.2f}s")
            else:
                raise ValueError("No duration specified and song duration not available")
        
        project.status = "planning"
        
        plan = await self.planner.create_plan(
            script=project.script,
            audio_analysis=project.audio_analysis or "",
            duration=duration
        )
        
        project.plan = plan
        project.status = "planned"
        
        return plan
    
    async def refine_plan(
        self,
        project_id: str,
        feedback: str
    ) -> MasterPlan:
        """
        Refine an existing plan based on user feedback.
        
        Args:
            project_id: The project to refine
            feedback: User feedback
        
        Returns:
            Refined MasterPlan
        """
        project = self._projects.get(project_id)
        if not project or not project.plan:
            raise ValueError(f"Project {project_id} not found or has no plan")
        
        refined_plan = await self.planner.refine_plan(project.plan, feedback)
        project.plan = refined_plan
        
        return refined_plan
    
    async def generate_media(
        self,
        project_id: str,
        on_progress: Optional[Callable[[int, int, MediaAsset], None]] = None
    ) -> list[MediaAsset]:
        """
        Generate all media assets for a project.
        
        Args:
            project_id: The project to generate media for
            on_progress: Optional callback for progress updates
        
        Returns:
            List of generated MediaAssets
        """
        project = self._projects.get(project_id)
        if not project or not project.plan:
            raise ValueError(f"Project {project_id} not found or has no plan")
        
        project.status = "generating"
        
        # Initialize generation status
        self._generation_status[project_id] = GenerationStatus(
            project_id=project_id,
            total_scenes=len(project.plan.scenes),
            completed_scenes=0,
            status="in_progress"
        )
        
        def progress_wrapper(scene_num: int, total: int, asset: MediaAsset):
            status = self._generation_status[project_id]
            status.completed_scenes = scene_num
            status.current_scene = scene_num
            status.assets.append(asset)
            
            if on_progress:
                on_progress(scene_num, total, asset)
        
        try:
            # Set style reference if project has one
            if project.style_reference:
                self.coordinator.set_style_reference(project.style_reference)
            
            assets = await self.coordinator.generate_all(
                scenes=project.plan.scenes,
                on_progress=progress_wrapper,
                style_reference=project.style_reference
            )
            
            project.assets = assets
            project.status = "ready"
            
            self._generation_status[project_id].status = "complete"
            
            return assets
            
        except Exception as e:
            project.status = "failed"
            self._generation_status[project_id].status = "failed"
            self._generation_status[project_id].error = str(e)
            raise
    
    def get_project(self, project_id: str) -> Optional[VideoProject]:
        """Get a project by ID"""
        return self._projects.get(project_id)
    
    def get_generation_status(self, project_id: str) -> Optional[GenerationStatus]:
        """Get generation status for a project"""
        return self._generation_status.get(project_id)
    
    async def run_full_pipeline(
        self,
        project_id: str,
        name: str,
        script: str,
        song_path: str,
        duration: float,
        on_progress: Optional[Callable] = None
    ) -> VideoProject:
        """
        Run the complete pipeline from script to generated assets.
        
        Args:
            project_id: Unique project identifier
            name: Project name
            script: Creative script
            song_path: Path to audio file
            duration: Video duration in seconds
            on_progress: Optional progress callback
        
        Returns:
            Completed VideoProject with all assets
        """
        # Create project
        project = await self.create_project(project_id, name, script, song_path)
        
        # Generate plan
        await self.generate_plan(project_id, duration)
        
        # Generate all media
        await self.generate_media(project_id, on_progress)
        
        return self._projects[project_id]
