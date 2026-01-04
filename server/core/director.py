"""
Final Director for Mourne.
Takes all generated media assets with stitching cards and produces
a MoviePy script for user approval and execution.

Features:
- Audio-synced transitions based on mood/energy
- Ken Burns with dynamic speed tied to scene mood
- Advanced color grading hints
- Beat-aware crossfades and cuts
"""
from typing import List, Optional
from .models import VideoProject, MediaAsset, MediaType, TransitionType, KenBurnsDirection
from .llm_backend import get_code_llm, OpenRouterLLM


DIRECTOR_SYSTEM_PROMPT = """You are an elite music video director and Python programmer specialized in MoviePy.
You create cinematic, emotionally-resonant video compositions that sync perfectly with audio.
Your code is production-quality: clean, well-commented, and handles edge cases.
You understand how to use transitions, zooms, and timing to create world-class trailers and music videos."""


DIRECTOR_PROMPT_TEMPLATE = """
Generate a complete, runnable Python script using MoviePy to assemble a cinematic music video.
You are a highly advanced visual engineer. If MoviePy lacks a built-in effect, you MUST implement it from scratch using `numpy`, `cv2` (OpenCV), or `scipy`.

**Project: {project_name}**
**Audio Track:** {song_path}
**Total Duration:** {total_duration} seconds

**User's Narrative Vision:**
{user_script}

**Assets and Stitching Cards:**
{assets_description}

**CINEMATIC EFFECTS LIBRARY:**
You have access to these concepts. Implement them creatively:

**1. Transitions (Motion & Optical):**
- *Standard:* Crossfade, Fade In/Out, Dip to Color (White/Black)
- *Motion:* Whip Pan (Fast directional blur), Slide, Push, Zoom-Through
- *Optical:* Luma Fade (Fade based on brightness), Glitch Transition (Digital artifacts), Flash Cut (Strobe)
- *Experimental:* Datamosh (Pixel bleeding), Slit-Scan (Time displacement), Pixel Sort (Sorting pixels by luminance)
- *Classic:* Match Cut (Visual similarity), Invisible Cut (Masking)

**2. Color Grading & Look Development:**
- *Techniques:* Bleach Bypass (High contrast, low saturation), Teal & Orange (Simulated split-toning), Cross-Processing (Shifted channels)
- *Atmosphere:* Day-for-Night (Blue tin, lower exp), Golden Hour (Warm gentle glow), Cyberpunk (Neon purples/greens)
- *Film Emulation:* 35mm Grain (Add noise), Halation (Glow on highlights), Gate Weave (Subtle camera shake)

**3. Visual FX (Compositing/Generative):**
- *Lens:* Chromatic Aberration (RGB channel shift), Vignetting (Dark corners), Lens Flare (Simulated overlays), Bokeh (Blur with mask)
- *Distortion:* VHS Tapes (Scanlines + noise), Heat Haze (Warping), Underwater (Sine wave distortion)
- *Lighting:* Volumetric Light Rays (Radial blur from highlights), Strobe/Flicker (Rhythmic opacity)

**DIRECTOR'S ALGORITHM:**

**A. Audio Analysis & Synchronization:**
- Sync hard cuts to Transients/Beats.
- Sync flowy transitions (dissolves) to Sustained Notes/Pads.
- Match "energy" of the visual effect to the audio amplitude.

**B. Scene Construction logic:**
1. **Asset Loading:** Load image/video.
2. **Pre-processing:** Resize to 1920x1080.
3. **Motion Design:** Apply Ken Burns (Pan/Zoom) for static images.
4. **Effect Layering:** Apply 1-3 visual effects from the library above based on the `mood`.
5. **Color Grading:** Apply the requested look.
6. **Transition-Out:** Prepare the clip for the next scene.

**C. Raw Implementation Guidelines:**
- **IF** a transition or effect exists in `moviepy.video.fx.all`, USE IT.
- **ELSE**, implement a custom FX function using `fl_image` or `make_frame`.
    - Example: Manual Chromatic Aberration in NumPy:
      ```python
      def chromatic_aberration(im, shift=2):
          r = np.roll(im[:,:,0], shift, axis=1)
          g = im[:,:,1]
          b = np.roll(im[:,:,2], -shift, axis=1)
          return np.stack([r,g,b], axis=2)
      ```
    - Example: Manual Flash:
      ```python
      def flash_effect(im, t):
          intensity = np.sin(t * 50) ** 2
          return np.clip(im * (1 + intensity), 0, 255)
      ```

**Output Structure:**
```python
#!/usr/bin/env python3
\"\"\"
Mourne Cinematic Director - Auto-Generated Script
Project: {project_name}
\"\"\"
from moviepy.editor import *
import moviepy.video.fx.all as vfx
import numpy as np
import cv2  # For advanced raw effects
import os

# [Configuration section]
# [Custom FX Library - Implement raw numpy/cv2 functions here]
# [Main assembly function]
# [Execution]
```

**Requirements:**
1. **Code Only:** Return ONLY the Python code.
2. **Robustness:** Handle potential errors (missing files).
3. **Length:** Ensure the video matches the audio duration EXACTLY.
4. **Complexity:** Do NOT be lazy. Use complex, raw effects if the mood calls for it.
"""


class Director:
    """
    The Final Director that assembles all media assets into a video processing script.
    The generated script syncs visuals with audio for cinematic results.
    """
    
    def __init__(self, llm: Optional[OpenRouterLLM] = None):
        self.llm = llm or get_code_llm()
    
    async def generate_processing_script(
        self,
        project: VideoProject,
        transition_duration: float = 0.5
    ) -> str:
        """
        Generate a MoviePy script to assemble the final video.
        
        Args:
            project: The video project with all assets
            transition_duration: Default duration of transitions in seconds
        
        Returns:
            Complete Python script as a string
        """
        if not project.assets:
            raise ValueError("Project has no generated assets")
        
        assets_description = self._format_assets_description(project.assets)
        total_duration = max(a.stitching_card.time_end for a in project.assets)
        
        prompt = DIRECTOR_PROMPT_TEMPLATE.format(
            project_name=project.name,
            song_path=project.song_path,
            total_duration=total_duration,
            user_script=project.script,
            assets_description=assets_description,
            transition_duration=transition_duration
        )
        
        script = await self.llm.generate(
            prompt=prompt,
            system=DIRECTOR_SYSTEM_PROMPT,
            temperature=0.25,
            max_tokens=12000
        )
        
        script = self._clean_script(script)
        project.processing_script = script
        
        return script
    
    def _format_assets_description(self, assets: List[MediaAsset]) -> str:
        """Format assets into detailed description for the prompt"""
        lines = []
        
        for asset in sorted(assets, key=lambda a: a.stitching_card.scene_number):
            card = asset.stitching_card
            
            # Format voice direction info
            voice_info = "No voice"
            if card.voice_direction and card.voice_direction.should_speak:
                vd = card.voice_direction
                voice_info = f"""Voice: {vd.voice_type.value}
    Dialogue: "{vd.dialogue_text or 'N/A'}"
    Tone: {vd.tone:.1f} | Cadence: {vd.cadence:.1f} | Warmth: {vd.warmth:.1f} | Solemnity: {vd.solemnity:.1f}
    Voice Profile: {vd.gender.value}, {vd.age_hint}
    Audio Path: {card.voice_audio_path or 'TO_BE_GENERATED'}
    Notes: {vd.voice_notes or 'None'}"""
            
            lines.append(f"""
Scene {card.scene_number}:
  - Type: {asset.media_type.value}
  - Path: {asset.asset_path}
  - Time: {card.time_start:.2f}s to {card.time_end:.2f}s (duration: {card.duration:.2f}s)
  - Transition In: {card.transition_in.value}
  - Transition Out: {card.transition_out.value}
  - Mood: {card.mood_description}
  - Color Grade Hint: {card.color_grade_hint or 'neutral'}
  - Ken Burns: {card.ken_burns_direction.value if card.ken_burns_direction else 'N/A'}
  - Audio Context: {card.audio_cue[:150]}...
  - {voice_info}
""")
        
        return "\n".join(lines)
    
    def _clean_script(self, script: str) -> str:
        """Clean up the generated script"""
        script = script.strip()
        
        if script.startswith("```python"):
            script = script[9:]
        elif script.startswith("```"):
            script = script[3:]
        
        if script.endswith("```"):
            script = script[:-3]
        
        return script.strip()
    
    def generate_static_script(
        self,
        project: VideoProject,
        transition_duration: float = 0.5
    ) -> str:
        """
        Generate a deterministic MoviePy script without LLM.
        Use this for consistent, predictable output.
        """
        assets = sorted(project.assets, key=lambda a: a.stitching_card.scene_number)
        
        asset_loads = []
        for i, asset in enumerate(assets):
            card = asset.stitching_card
            
            # Determine transition speed based on mood
            trans_dur = self._mood_to_transition_duration(card.mood_description, transition_duration)
            
            if asset.media_type == MediaType.IMAGE:
                kb_dir = card.ken_burns_direction.value if card.ken_burns_direction else 'zoom_in'
                kb_intensity = self._mood_to_ken_burns_intensity(card.mood_description)
                color_fx = self._color_grade_to_fx(card.color_grade_hint)
                
                asset_loads.append(f'''
    # Scene {card.scene_number}: {card.mood_description}
    clip_{i} = create_ken_burns(
        r"{asset.asset_path}",
        duration={card.duration:.2f},
        direction="{kb_dir}",
        intensity={kb_intensity},
        resolution=TARGET_RESOLUTION
    )
    clip_{i} = apply_color_grade(clip_{i}, "{card.color_grade_hint or 'neutral'}")
    scene_transitions.append({trans_dur})''')
            else:
                asset_loads.append(f'''
    # Scene {card.scene_number}: {card.mood_description}
    clip_{i} = VideoFileClip(r"{asset.asset_path}")
    clip_{i} = clip_{i}.resize(TARGET_RESOLUTION)
    target_duration = {card.duration:.2f}
    if clip_{i}.duration != target_duration:
        clip_{i} = clip_{i}.fx(vfx.speedx, clip_{i}.duration / target_duration)
    clip_{i} = apply_color_grade(clip_{i}, "{card.color_grade_hint or 'neutral'}")
    scene_transitions.append({trans_dur})''')
        
        clip_names = [f"clip_{i}" for i in range(len(assets))]
        
        script = f'''#!/usr/bin/env python3
"""
Mourne Cinematic Director - Auto-Generated Script
Project: {project.name}
Generated Assets: {len(assets)}
"""
from moviepy.editor import *
import moviepy.video.fx.all as vfx
import numpy as np
import os

# Configuration
OUTPUT_PATH = "final_{project.id}.mp4"
AUDIO_PATH = r"{project.song_path}"
TARGET_RESOLUTION = (1920, 1080)
FPS = 30

def create_ken_burns(image_path, duration, direction, intensity, resolution):
    """
    Apply Ken Burns effect with variable intensity.
    intensity: 0.05 = subtle, 0.15 = strong
    """
    img = ImageClip(image_path)
    
    # Scale to fit with headroom for movement
    scale_factor = max(resolution[0] / img.w, resolution[1] / img.h) * (1 + intensity)
    img = img.resize(scale_factor)
    
    w, h = img.size
    cx, cy = w / 2, h / 2
    
    def zoom_effect(get_frame, t):
        progress = t / duration
        
        if direction == "zoom_in":
            scale = 1 + progress * intensity
        elif direction == "zoom_out":
            scale = (1 + intensity) - progress * intensity
        elif direction == "pan_right":
            return get_frame(t)
        elif direction == "pan_left":
            return get_frame(t)
        else:
            scale = 1 + progress * intensity
        
        return get_frame(t)
    
    if direction == "zoom_in":
        img = img.resize(lambda t: 1 + (t / duration) * intensity)
    elif direction == "zoom_out":
        img = img.resize(lambda t: (1 + intensity) - (t / duration) * intensity)
    elif direction == "pan_right":
        img = img.set_position(lambda t: (-intensity * resolution[0] + (t / duration) * intensity * 2 * resolution[0], 'center'))
    elif direction == "pan_left":
        img = img.set_position(lambda t: (intensity * resolution[0] - (t / duration) * intensity * 2 * resolution[0], 'center'))
    elif direction == "pan_up":
        img = img.set_position(lambda t: ('center', intensity * resolution[1] - (t / duration) * intensity * 2 * resolution[1]))
    elif direction == "pan_down":
        img = img.set_position(lambda t: ('center', -intensity * resolution[1] + (t / duration) * intensity * 2 * resolution[1]))
    
    img = img.set_duration(duration)
    bg = ColorClip(resolution, color=(0, 0, 0)).set_duration(duration)
    final = CompositeVideoClip([bg, img.set_position('center')], size=resolution)
    
    return final


def apply_color_grade(clip, grade):
    """Apply color grading based on mood hint."""
    if grade == "warm_orange":
        return clip.fx(vfx.colorx, 1.1)
    elif grade == "cool_blue":
        return clip.fx(vfx.colorx, 0.9)
    elif grade == "desaturated_dark":
        return clip.fx(vfx.colorx, 0.7).fx(vfx.lum_contrast, contrast=0.1)
    elif grade == "saturated_vivid":
        return clip.fx(vfx.colorx, 1.2)
    elif grade == "soft_pastel":
        return clip.fx(vfx.colorx, 1.05)
    return clip


def assemble_with_transitions(clips, transition_durations):
    """Assemble clips with variable-length crossfades."""
    if len(clips) == 0:
        return None
    if len(clips) == 1:
        return clips[0]
    
    # Build composition with overlapping transitions
    result_clips = [clips[0]]
    current_time = clips[0].duration
    
    for i, clip in enumerate(clips[1:], 1):
        trans_dur = transition_durations[i] if i < len(transition_durations) else 0.5
        # Overlap with previous clip
        offset = current_time - trans_dur
        clip = clip.set_start(offset).crossfadein(trans_dur)
        result_clips.append(clip)
        current_time = offset + clip.duration
    
    return CompositeVideoClip(result_clips)


def main():
    print("=" * 60)
    print("MOURNE CINEMATIC DIRECTOR")
    print(f"Project: {project.name}")
    print("=" * 60)
    
    clips = []
    scene_transitions = []
    
{chr(10).join(asset_loads)}
    
    clips = [{", ".join(clip_names)}]
    
    print(f"\\nLoaded {{len(clips)}} clips")
    
    # Assemble with mood-aware transitions
    print("Assembling with cinematic transitions...")
    final_video = assemble_with_transitions(clips, scene_transitions)
    
    # Add audio
    print("Syncing audio track...")
    if os.path.exists(AUDIO_PATH):
        audio = AudioFileClip(AUDIO_PATH)
        if audio.duration > final_video.duration:
            audio = audio.subclip(0, final_video.duration)
        final_video = final_video.set_audio(audio)
    else:
        print(f"Warning: Audio not found at {{AUDIO_PATH}}")
    
    # Render
    print("\\nRendering final video...")
    print(f"Output: {{OUTPUT_PATH}}")
    
    final_video.write_videofile(
        OUTPUT_PATH,
        fps=FPS,
        codec='libx264',
        audio_codec='aac',
        threads=4,
        preset='medium',
        logger='bar'
    )
    
    print("\\n" + "=" * 60)
    print(f"COMPLETE: {{OUTPUT_PATH}}")
    print("=" * 60)
    
    final_video.close()


if __name__ == "__main__":
    main()
'''
        
        return script
    
    def _mood_to_transition_duration(self, mood: str, default: float) -> float:
        """Calculate transition duration based on mood."""
        mood_lower = mood.lower()
        
        if any(m in mood_lower for m in ["energetic", "upbeat", "fast", "intense"]):
            return 0.25
        elif any(m in mood_lower for m in ["epic", "climactic", "powerful"]):
            return 0.4
        elif any(m in mood_lower for m in ["emotional", "intimate", "gentle", "tender"]):
            return 1.0
        elif any(m in mood_lower for m in ["dreamy", "ethereal", "peaceful"]):
            return 1.5
        else:
            return default
    
    def _mood_to_ken_burns_intensity(self, mood: str) -> float:
        """Calculate Ken Burns zoom intensity based on mood."""
        mood_lower = mood.lower()
        
        if any(m in mood_lower for m in ["epic", "climactic", "intense"]):
            return 0.15
        elif any(m in mood_lower for m in ["energetic", "upbeat", "dynamic"]):
            return 0.12
        elif any(m in mood_lower for m in ["dreamy", "peaceful", "gentle"]):
            return 0.05
        else:
            return 0.08
    
    def _color_grade_to_fx(self, grade: Optional[str]) -> str:
        """Get MoviePy fx call for color grade."""
        fx_map = {
            "warm_orange": "colorx(1.1)",
            "cool_blue": "colorx(0.9)",
            "desaturated_dark": "colorx(0.7)",
            "saturated_vivid": "colorx(1.2)",
            "soft_pastel": "colorx(1.05)"
        }
        return fx_map.get(grade, "colorx(1.0)")
    
    async def save_script(
        self,
        project: VideoProject,
        output_path: str
    ) -> str:
        """Generate and save the processing script to a file."""
        if not project.processing_script:
            await self.generate_processing_script(project)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(project.processing_script)
        
        return output_path
