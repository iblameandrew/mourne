"""
Core data models for the Mourne media generation pipeline.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class StyleReference(BaseModel):
    """Extracted style descriptors from a reference image"""
    artistic_style: str = Field(default="photorealistic", description="e.g., photorealistic, anime, oil painting")
    rendering_technique: str = Field(default="cinematic", description="e.g., cel-shaded, hyperrealistic")
    color_palette: str = Field(default="natural colors", description="Dominant colors and harmony")
    lighting_style: str = Field(default="natural lighting", description="e.g., golden hour, neon, chiaroscuro")
    texture_quality: str = Field(default="detailed", description="e.g., smooth, grainy, painterly")
    mood: str = Field(default="neutral", description="Emotional tone")
    atmosphere: str = Field(default="clear", description="e.g., foggy, crisp, dreamlike")
    composition_notes: str = Field(default="balanced", description="Notable composition techniques")
    detail_level: str = Field(default="moderate detail", description="e.g., highly detailed, minimalist")
    style_prompt: str = Field(default="", description="Concise style directive to inject into prompts")
    source_image_path: Optional[str] = None


class MediaType(str, Enum):
    """Type of media asset"""
    IMAGE = "image"
    VIDEO = "video"


class TransitionType(str, Enum):
    """Video transition types"""
    FADE = "fade"
    CROSSFADE = "crossfade"
    CUT = "cut"
    ZOOM = "zoom"
    SLIDE = "slide"


class KenBurnsDirection(str, Enum):
    """Ken Burns effect directions for static images"""
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"
    PAN_UP = "pan_up"
    PAN_DOWN = "pan_down"


class VoiceType(str, Enum):
    """Type of voice overlay for a scene"""
    NARRATOR = "narrator"           # Omniscient storytelling voice
    CHARACTER = "character"         # Entity/character speaking
    INNER_THOUGHT = "inner_thought" # Internal monologue
    NONE = "none"                   # No voice for this scene


class VoiceGender(str, Enum):
    """Voice gender profile"""
    MASCULINE = "masculine"
    FEMININE = "feminine"
    ANDROGYNOUS = "androgynous"


class VoiceDirection(BaseModel):
    """
    Voice calibration for a scene.
    Determines if entities speak, what voice type, and detailed voice parameters.
    """
    voice_type: VoiceType = VoiceType.NONE
    should_speak: bool = False
    
    # Voice characteristics (0.0 to 1.0 scale)
    tone: float = Field(default=0.5, ge=0.0, le=1.0, description="0=dark/serious, 1=bright/uplifting")
    cadence: float = Field(default=0.5, ge=0.0, le=1.0, description="0=slow/deliberate, 1=fast/energetic")
    warmth: float = Field(default=0.5, ge=0.0, le=1.0, description="0=cold/distant, 1=warm/intimate")
    solemnity: float = Field(default=0.5, ge=0.0, le=1.0, description="0=casual/playful, 1=solemn/reverent")
    
    # Voice profile
    gender: VoiceGender = VoiceGender.ANDROGYNOUS
    age_hint: str = Field(default="adult", description="young, adult, elderly")
    accent_hint: Optional[str] = None
    
    # Content
    dialogue_text: Optional[str] = Field(default=None, description="What to say if should_speak=True")
    voice_notes: Optional[str] = Field(default=None, description="Director notes for voice delivery")


class StitchingCard(BaseModel):
    """
    Metadata attached to each generated media asset.
    Contains all information needed for the final video assembly.
    """
    id: str
    scene_number: int
    time_start: float
    time_end: float
    visual_prompt: str = Field(description="The exact prompt used to generate this media")
    audio_cue: str = Field(description="Lyrics/audio description at this timestamp")
    mood_description: str = Field(description="Emotional tone of this scene")
    transition_in: TransitionType = TransitionType.CROSSFADE
    transition_out: TransitionType = TransitionType.CROSSFADE
    transition_duration: float = 0.5
    ken_burns_direction: Optional[KenBurnsDirection] = None
    color_grade_hint: Optional[str] = None  # e.g., "warm", "cold", "desaturated"
    voice_direction: Optional[VoiceDirection] = Field(default=None, description="Voice calibration for this scene")
    voice_audio_path: Optional[str] = Field(default=None, description="Path to generated voice audio clip")
    
    @property
    def duration(self) -> float:
        return self.time_end - self.time_start


class MediaAsset(BaseModel):
    """A generated media file with its stitching card"""
    asset_path: str = Field(description="Local path to the generated file")
    media_type: MediaType
    stitching_card: StitchingCard
    generation_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="API response info, model used, generation params"
    )


class SceneStep(BaseModel):
    """A single granular step from the Master Planner"""
    scene_number: int
    description: str = Field(description="Brief narrative description of the scene")
    time_start: float
    time_end: float
    suggested_media_type: MediaType
    visual_prompt_draft: str = Field(description="Initial visual prompt for refinement")
    audio_context: str = Field(description="What's happening in the audio at this moment")
    mood: str = Field(description="Emotional tone (e.g., melancholic, energetic, ethereal)")
    suggested_transition: Optional[TransitionType] = TransitionType.CROSSFADE
    voice_direction: Optional[VoiceDirection] = Field(default=None, description="Voice orchestration for this scene")
    
    @property
    def duration(self) -> float:
        return self.time_end - self.time_start


class MasterPlan(BaseModel):
    """Complete plan output from the Master Planner"""
    project_name: str
    total_duration: float
    scenes: List[SceneStep]
    
    def validate_coverage(self) -> bool:
        """Ensure scenes cover the entire duration without gaps"""
        if not self.scenes:
            return False
        
        sorted_scenes = sorted(self.scenes, key=lambda s: s.time_start)
        
        # Check first scene starts at 0
        if sorted_scenes[0].time_start > 0.5:  # Allow 0.5s tolerance
            return False
        
        # Check for gaps between scenes
        for i in range(len(sorted_scenes) - 1):
            gap = sorted_scenes[i + 1].time_start - sorted_scenes[i].time_end
            if gap > 0.5:  # More than 0.5s gap
                return False
        
        # Check last scene ends at total duration
        if abs(sorted_scenes[-1].time_end - self.total_duration) > 1.0:
            return False
        
        return True


class VideoProject(BaseModel):
    """Complete project ready for the Final Director"""
    id: str
    name: str
    script: str
    song_path: str
    song_duration: Optional[float] = Field(default=None, description="Duration of the audio track in seconds")
    audio_analysis: Optional[str] = None
    style_reference: Optional[StyleReference] = Field(default=None, description="Visual style from reference image")
    plan: Optional[MasterPlan] = None
    assets: List[MediaAsset] = Field(default_factory=list)
    processing_script: Optional[str] = None
    status: str = "created"  # created, planning, generating, ready, rendering, complete
    
    def is_ready_for_director(self) -> bool:
        """Check if all assets are generated and ready for final assembly"""
        if not self.plan:
            return False
        return len(self.assets) == len(self.plan.scenes)


class GenerationStatus(BaseModel):
    """Status of the media generation process"""
    project_id: str
    total_scenes: int
    completed_scenes: int
    current_scene: Optional[int] = None
    status: str  # pending, in_progress, complete, failed
    error: Optional[str] = None
    assets: List[MediaAsset] = Field(default_factory=list)
    
    @property
    def progress_percent(self) -> float:
        if self.total_scenes == 0:
            return 0.0
        return (self.completed_scenes / self.total_scenes) * 100
