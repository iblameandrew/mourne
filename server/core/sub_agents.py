"""
Sub-agents for Mourne media generation pipeline.
Specialized agents that refine prompts and generate media assets with stitching cards.
"""
import os
import uuid
from typing import Optional, List
from .llm_backend import get_creative_llm, OpenRouterLLM
from .media_backends import GeminiImageBackend, VeoVideoBackend, MediaBackendManager
from .models import (
    SceneStep, 
    MediaAsset, 
    StitchingCard, 
    MediaType,
    TransitionType,
    KenBurnsDirection
)


PROMPT_REFINER_SYSTEM = """You are an expert prompt engineer for AI image and video generation.
Your job is to transform draft prompts into production-quality prompts that will generate stunning visuals.
You understand cinematography, lighting, composition, and artistic styles deeply."""


PROMPT_REFINER_TEMPLATE = """
Refine this draft prompt into a production-quality prompt optimized for {media_type} generation.

**Draft Prompt:** 
{draft_prompt}

**Scene Context:**
- Description: {description}
- Mood: {mood}
- Audio Context: {audio_context}
- Duration: {duration} seconds

**Guidelines for {media_type} prompts:**

For IMAGES:
- Focus on composition (rule of thirds, leading lines, symmetry)
- Specify lighting (golden hour, blue hour, neon, rim lighting, volumetric)
- Define color palette (warm earth tones, cool blues, high contrast)
- Camera angle (low angle hero shot, bird's eye, intimate close-up)
- Artistic style (photorealistic, cinematic film grain, anime, baroque)
- Atmosphere (foggy, dusty, lens flare, bokeh)

For VIDEOS:
- Include motion descriptions (slow dolly forward, orbital shot, parallax)
- Camera movements (tracking shot, crane up, steadicam follow)
- Temporal flow (time-lapse, slow motion, real-time)
- Subject motion (walking into frame, turning to face camera)
- Environmental motion (leaves falling, smoke rising, waves crashing)

**Requirements:**
- Be SPECIFIC and EVOCATIVE, not generic
- Include technical cinematography terms
- Match the mood precisely
- The prompt should evoke a single, clear visual

Return ONLY the refined prompt text. No explanation, no quotes, just the prompt.
"""


class PromptRefinerAgent:
    """Refines draft prompts into production-quality generation prompts"""
    
    def __init__(self, llm: Optional[OpenRouterLLM] = None):
        self.llm = llm or get_creative_llm()
    
    async def refine(self, scene: SceneStep) -> str:
        """
        Refine a scene's draft prompt into a production-quality prompt.
        
        Args:
            scene: The scene step with draft prompt
        
        Returns:
            Refined prompt string
        """
        prompt = PROMPT_REFINER_TEMPLATE.format(
            media_type=scene.suggested_media_type.value.upper(),
            draft_prompt=scene.visual_prompt_draft,
            description=scene.description,
            mood=scene.mood,
            audio_context=scene.audio_context,
            duration=scene.duration
        )
        
        refined = await self.llm.generate(
            prompt=prompt,
            system=PROMPT_REFINER_SYSTEM,
            temperature=0.85
        )
        
        # Clean up response (remove quotes if wrapped)
        refined = refined.strip().strip('"').strip("'")
        
        return refined


class ImageGeneratorAgent:
    """Generates images via Gemini and attaches stitching cards"""
    
    def __init__(
        self, 
        output_dir: str = "generated_media",
        image_backend: Optional[GeminiImageBackend] = None,
        prompt_refiner: Optional[PromptRefinerAgent] = None
    ):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.backend = image_backend or MediaBackendManager.get_image_backend()
        self.prompt_refiner = prompt_refiner or PromptRefinerAgent()
    
    async def generate(self, scene: SceneStep) -> MediaAsset:
        """
        Generate an image for a scene and create its stitching card.
        
        Args:
            scene: The scene step to generate media for
        
        Returns:
            MediaAsset with generated image and stitching card
        """
        # Refine the prompt
        refined_prompt = await self.prompt_refiner.refine(scene)
        
        # Generate unique filename
        asset_id = str(uuid.uuid4())[:8]
        output_path = os.path.join(
            self.output_dir, 
            f"scene_{scene.scene_number:03d}_{asset_id}"
        )
        
        # Generate the image
        final_path = await self.backend.generate_image(refined_prompt, output_path)
        
        # Determine Ken Burns direction based on mood
        ken_burns = self._select_ken_burns(scene.mood)
        
        # Parse transition
        transition = self._parse_transition(scene.suggested_transition)
        
        # Create stitching card
        card = StitchingCard(
            id=asset_id,
            scene_number=scene.scene_number,
            time_start=scene.time_start,
            time_end=scene.time_end,
            visual_prompt=refined_prompt,
            audio_cue=scene.audio_context,
            mood_description=scene.mood,
            transition_in=transition,
            transition_out=transition,
            ken_burns_direction=ken_burns,
            color_grade_hint=self._mood_to_color_grade(scene.mood)
        )
        
        return MediaAsset(
            asset_path=final_path,
            media_type=MediaType.IMAGE,
            stitching_card=card,
            generation_metadata={
                "model": "gemini-3-pro-image-preview",
                "prompt": refined_prompt,
                "original_prompt": scene.visual_prompt_draft
            }
        )
    
    def _select_ken_burns(self, mood: str) -> KenBurnsDirection:
        """Select Ken Burns direction based on mood"""
        mood_lower = mood.lower()
        
        if any(word in mood_lower for word in ["epic", "grand", "triumphant", "powerful"]):
            return KenBurnsDirection.ZOOM_OUT
        elif any(word in mood_lower for word in ["intimate", "personal", "emotional", "tender"]):
            return KenBurnsDirection.ZOOM_IN
        elif any(word in mood_lower for word in ["journey", "movement", "travel"]):
            return KenBurnsDirection.PAN_RIGHT
        elif any(word in mood_lower for word in ["ascending", "hopeful", "rising"]):
            return KenBurnsDirection.PAN_UP
        else:
            return KenBurnsDirection.ZOOM_IN  # Default
    
    def _parse_transition(self, transition: Optional[str]) -> TransitionType:
        """Parse transition string to enum"""
        if not transition:
            return TransitionType.CROSSFADE
        
        transition_map = {
            "fade": TransitionType.FADE,
            "crossfade": TransitionType.CROSSFADE,
            "cut": TransitionType.CUT,
            "zoom": TransitionType.ZOOM,
            "slide": TransitionType.SLIDE
        }
        return transition_map.get(transition.lower(), TransitionType.CROSSFADE)
    
    def _mood_to_color_grade(self, mood: str) -> str:
        """Suggest color grading based on mood"""
        mood_lower = mood.lower()
        
        if any(word in mood_lower for word in ["warm", "nostalgic", "golden", "sunset"]):
            return "warm_orange"
        elif any(word in mood_lower for word in ["cold", "melancholic", "sad", "lonely"]):
            return "cool_blue"
        elif any(word in mood_lower for word in ["dark", "mysterious", "ominous"]):
            return "desaturated_dark"
        elif any(word in mood_lower for word in ["vibrant", "energetic", "happy", "joyful"]):
            return "saturated_vivid"
        elif any(word in mood_lower for word in ["dreamy", "ethereal", "surreal"]):
            return "soft_pastel"
        else:
            return "neutral"


class VideoGeneratorAgent:
    """Generates videos via Veo and attaches stitching cards"""
    
    def __init__(
        self, 
        output_dir: str = "generated_media",
        video_backend: Optional[VeoVideoBackend] = None,
        prompt_refiner: Optional[PromptRefinerAgent] = None
    ):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.backend = video_backend or MediaBackendManager.get_video_backend()
        self.prompt_refiner = prompt_refiner or PromptRefinerAgent()
    
    async def generate(self, scene: SceneStep) -> MediaAsset:
        """
        Generate a video for a scene and create its stitching card.
        
        Args:
            scene: The scene step to generate media for
        
        Returns:
            MediaAsset with generated video and stitching card
        """
        # Refine the prompt
        refined_prompt = await self.prompt_refiner.refine(scene)
        
        # Calculate duration (clamped to Veo limits: 4, 6, or 8 seconds)
        raw_duration = scene.duration
        if raw_duration <= 5:
            duration = 4
        elif raw_duration <= 7:
            duration = 6
        else:
            duration = 8
        
        # Generate unique filename
        asset_id = str(uuid.uuid4())[:8]
        output_path = os.path.join(
            self.output_dir, 
            f"scene_{scene.scene_number:03d}_{asset_id}.mp4"
        )
        
        # Generate the video
        final_path = await self.backend.generate_video(
            prompt=refined_prompt, 
            output_path=output_path,
            duration_seconds=duration
        )
        
        # Parse transition
        transition = self._parse_transition(scene.suggested_transition)
        
        # Create stitching card
        card = StitchingCard(
            id=asset_id,
            scene_number=scene.scene_number,
            time_start=scene.time_start,
            time_end=scene.time_end,
            visual_prompt=refined_prompt,
            audio_cue=scene.audio_context,
            mood_description=scene.mood,
            transition_in=transition,
            transition_out=transition,
            ken_burns_direction=None,  # Not applicable for video
            color_grade_hint=self._mood_to_color_grade(scene.mood)
        )
        
        return MediaAsset(
            asset_path=final_path,
            media_type=MediaType.VIDEO,
            stitching_card=card,
            generation_metadata={
                "model": "veo-3.1-generate-preview",
                "prompt": refined_prompt,
                "original_prompt": scene.visual_prompt_draft,
                "requested_duration": duration,
                "scene_duration": scene.duration
            }
        )
    
    def _parse_transition(self, transition: Optional[str]) -> TransitionType:
        """Parse transition string to enum"""
        if not transition:
            return TransitionType.CROSSFADE
        
        transition_map = {
            "fade": TransitionType.FADE,
            "crossfade": TransitionType.CROSSFADE,
            "cut": TransitionType.CUT,
            "zoom": TransitionType.ZOOM,
            "slide": TransitionType.SLIDE
        }
        return transition_map.get(transition.lower(), TransitionType.CROSSFADE)
    
    def _mood_to_color_grade(self, mood: str) -> str:
        """Suggest color grading based on mood"""
        mood_lower = mood.lower()
        
        if any(word in mood_lower for word in ["warm", "nostalgic", "golden", "sunset"]):
            return "warm_orange"
        elif any(word in mood_lower for word in ["cold", "melancholic", "sad", "lonely"]):
            return "cool_blue"
        elif any(word in mood_lower for word in ["dark", "mysterious", "ominous"]):
            return "desaturated_dark"
        elif any(word in mood_lower for word in ["vibrant", "energetic", "happy", "joyful"]):
            return "saturated_vivid"
        elif any(word in mood_lower for word in ["dreamy", "ethereal", "surreal"]):
            return "soft_pastel"
        else:
            return "neutral"


class ImageToVideoAgent:
    """Animates an existing image asset into a video"""
    
    def __init__(
        self, 
        output_dir: str = "generated_media",
        video_backend: Optional[VeoVideoBackend] = None,
        prompt_refiner: Optional[PromptRefinerAgent] = None
    ):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.backend = video_backend or MediaBackendManager.get_video_backend()
        self.prompt_refiner = prompt_refiner or PromptRefinerAgent()
    
    async def animate(self, scene: SceneStep, image_asset: MediaAsset) -> MediaAsset:
        """
        Produce a video from an image asset.
        
        Args:
            scene: The scene step
            image_asset: The previously generated image
        
        Returns:
            New MediaAsset (video)
        """
        # We can use the refined prompt from the image or refine a new one for motion
        prompt = image_asset.stitching_card.visual_prompt
        
        # Add motion cues to prompt
        motion_prompt = f"{prompt}, subtle cinematic motion, parallax effect, professional camera movement"
        
        # Calculate duration
        raw_duration = scene.duration
        if raw_duration <= 5:
            duration = 4
        elif raw_duration <= 7:
            duration = 6
        else:
            duration = 8
        
        # Generate unique filename
        asset_id = str(uuid.uuid4())[:8]
        output_path = os.path.join(
            self.output_dir, 
            f"scene_{scene.scene_number:03d}_animated_{asset_id}.mp4"
        )
        
        # Generate the video from image
        final_path = await self.backend.generate_video(
            prompt=motion_prompt, 
            output_path=output_path,
            input_image_path=image_asset.asset_path,
            duration_seconds=duration
        )
        
        # Create new stitching card based on the image's card
        image_card = image_asset.stitching_card
        card = StitchingCard(
            id=asset_id,
            scene_number=scene.scene_number,
            time_start=scene.time_start,
            time_end=scene.time_end,
            visual_prompt=motion_prompt,
            audio_cue=image_card.audio_cue,
            mood_description=image_card.mood_description,
            transition_in=image_card.transition_in,
            transition_out=image_card.transition_out,
            ken_burns_direction=None,
            color_grade_hint=image_card.color_grade_hint
        )
        
        return MediaAsset(
            asset_path=final_path,
            media_type=MediaType.VIDEO,
            stitching_card=card,
            generation_metadata={
                "model": "veo-image2video" if hasattr(self.backend, 'model') and "veo" in str(self.backend.model) else "svd-image2video",
                "prompt": motion_prompt,
                "input_image": image_asset.asset_path,
                "requested_duration": duration
            }
        )


class MediaGenerationCoordinator:
    """
    Coordinates the generation of all media assets for a plan.
    Dispatches to appropriate agents based on media type.
    Includes dynamic Image2Video logic.
    """
    
    def __init__(
        self,
        output_dir: str = "generated_media",
        image_agent: Optional[ImageGeneratorAgent] = None,
        video_agent: Optional[VideoGeneratorAgent] = None,
        i2v_agent: Optional[ImageToVideoAgent] = None
    ):
        self.output_dir = output_dir
        self.image_agent = image_agent or ImageGeneratorAgent(output_dir)
        self.video_agent = video_agent or VideoGeneratorAgent(output_dir)
        self.i2v_agent = i2v_agent or ImageToVideoAgent(output_dir)
    
    async def generate_all(
        self, 
        scenes: List[SceneStep],
        on_progress: Optional[callable] = None
    ) -> List[MediaAsset]:
        """
        Generate media for all scenes in a plan.
        
        Args:
            scenes: List of scene steps to generate
            on_progress: Optional callback(scene_number, total, asset)
        
        Returns:
            List of generated MediaAssets
        """
        assets = []
        total = len(scenes)
        
        for scene in scenes:
            print(f"Generating scene {scene.scene_number}/{total}: {scene.description[:50]}...")
            
            try:
                asset = None
                
                # Dynamic Logic: Decide when to use Image2Video
                # If scene suggests video but we want maximum control, 
                # or if the user/orchestrator specifically flags it.
                # Here we implement the logic: If it's a VIDEO scene AND 
                # it's a "scenic/artistic" mood, we might produce an image first.
                
                should_image_to_video = False
                if scene.suggested_media_type == MediaType.VIDEO:
                    # Heuristic: Animate if mood is cinematic or artistic
                    cinematic_moods = ["epic", "cinematic", "painterly", "dreamy", "scenic"]
                    if any(m in scene.mood.lower() for m in cinematic_moods):
                        should_image_to_video = True
                
                if should_image_to_video:
                    # Step 1: Generate high-quality Image
                    img_asset = await self.image_agent.generate(scene)
                    # Notify progress for the image (optional, or wait for video)
                    if on_progress:
                        on_progress(scene.scene_number, total, img_asset)
                    
                    # Step 2: Animate the Image
                    print(f"  --> Animating image for scene {scene.scene_number}...")
                    asset = await self.i2v_agent.animate(scene, img_asset)
                elif scene.suggested_media_type == MediaType.IMAGE:
                    asset = await self.image_agent.generate(scene)
                else:
                    asset = await self.video_agent.generate(scene)
                
                assets.append(asset)
                
                if on_progress:
                    on_progress(scene.scene_number, total, asset)
                    
            except Exception as e:
                print(f"Error generating scene {scene.scene_number}: {e}")
                raise
        
        # Sort by scene number to ensure correct order
        assets.sort(key=lambda a: a.stitching_card.scene_number)
        
        return assets
