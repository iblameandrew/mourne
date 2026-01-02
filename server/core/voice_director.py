"""
Voice Director for Mourne.
Analyzes scenes and determines voice orchestration - who speaks, when, and how.
Calibrates tone, cadence, warmth, and solemnity for each scene.
"""
import json
from typing import List, Optional
from .llm_backend import get_planner_llm, OpenRouterLLM
from .models import (
    SceneStep, MasterPlan, VoiceDirection, VoiceType, VoiceGender
)


VOICE_DIRECTOR_SYSTEM_PROMPT = """You are an expert Voice Director for cinematic productions.
You analyze scenes and determine:
1. Whether a scene needs voice (narration, character dialogue, inner thought, or silence)
2. The exact calibration of voice parameters to match the emotional arc
3. What dialogue or narration text fits the scene

You understand the power of silence - not every scene needs voice.
You understand narrative pacing - voice should enhance, not overwhelm.
You create voice direction that syncs with music and visuals emotionally."""


VOICE_ANALYSIS_PROMPT = """
Analyze the following video project and determine voice direction for each scene.

**User's Creative Vision:**
{user_script}

**Project Name:** {project_name}
**Total Duration:** {total_duration} seconds

**Scenes:**
{scenes_description}

For each scene, determine:
1. **should_speak**: Does this scene need voice? (Consider: Does silence enhance this moment?)
2. **voice_type**: "narrator" (omniscient), "character" (entity speaking), "inner_thought" (internal monologue), or "none"
3. **tone**: 0.0 (dark/serious) to 1.0 (bright/uplifting)
4. **cadence**: 0.0 (slow/deliberate) to 1.0 (fast/energetic) 
5. **warmth**: 0.0 (cold/distant) to 1.0 (warm/intimate)
6. **solemnity**: 0.0 (casual/playful) to 1.0 (solemn/reverent)
7. **gender**: "masculine", "feminine", or "androgynous"
8. **age_hint**: "young", "adult", or "elderly"
9. **dialogue_text**: If speaking, the exact text to say (match scene duration!)
10. **voice_notes**: Director notes for delivery style

**Guidelines:**
- Match voice parameters to scene mood and audio context
- Vary voice presence - silence is powerful
- Ensure dialogue length fits the scene duration
- Build emotional arc across scenes (don't always use same parameters)
- Inner thoughts work well for intimate, reflective moments
- Narrator works for establishing shots and transitions
- Character voice for direct address or dialogue moments

Return JSON array with one object per scene:
[
  {{
    "scene_number": 1,
    "should_speak": true,
    "voice_type": "narrator",
    "tone": 0.3,
    "cadence": 0.4,
    "warmth": 0.6,
    "solemnity": 0.7,
    "gender": "feminine",
    "age_hint": "adult",
    "dialogue_text": "In the depths of winter...",
    "voice_notes": "Hushed, reverent, slight echo"
  }},
  ...
]

Return ONLY valid JSON. No explanation, no markdown code blocks.
"""


class VoiceDirector:
    """
    Analyzes scenes and determines voice orchestration.
    Decides: who speaks, when, with what tone/cadence/warmth/solemnity.
    """
    
    def __init__(self, llm: Optional[OpenRouterLLM] = None):
        self.llm = llm or get_planner_llm()
    
    async def generate_voice_plan(
        self,
        plan: MasterPlan,
        project_script: str
    ) -> List[VoiceDirection]:
        """
        Generate voice directions for entire project.
        Ensures coherent voice arc across scenes.
        
        Args:
            plan: The master plan with all scenes
            project_script: The user's original creative script
        
        Returns:
            List of VoiceDirection objects, one per scene
        """
        scenes_description = self._format_scenes_description(plan.scenes)
        
        prompt = VOICE_ANALYSIS_PROMPT.format(
            user_script=project_script,
            project_name=plan.project_name,
            total_duration=plan.total_duration,
            scenes_description=scenes_description
        )
        
        result = await self.llm.generate_json(
            prompt=prompt,
            system=VOICE_DIRECTOR_SYSTEM_PROMPT,
            temperature=0.6
        )
        
        # Parse results into VoiceDirection objects
        voice_directions = []
        
        # Handle both list and dict responses
        if isinstance(result, dict) and "scenes" in result:
            result = result["scenes"]
        
        for voice_data in result:
            try:
                # Parse voice type
                voice_type_str = voice_data.get("voice_type", "none").lower()
                voice_type_map = {
                    "narrator": VoiceType.NARRATOR,
                    "character": VoiceType.CHARACTER,
                    "inner_thought": VoiceType.INNER_THOUGHT,
                    "none": VoiceType.NONE
                }
                voice_type = voice_type_map.get(voice_type_str, VoiceType.NONE)
                
                # Parse gender
                gender_str = voice_data.get("gender", "androgynous").lower()
                gender_map = {
                    "masculine": VoiceGender.MASCULINE,
                    "feminine": VoiceGender.FEMININE,
                    "androgynous": VoiceGender.ANDROGYNOUS
                }
                gender = gender_map.get(gender_str, VoiceGender.ANDROGYNOUS)
                
                direction = VoiceDirection(
                    voice_type=voice_type,
                    should_speak=voice_data.get("should_speak", False),
                    tone=self._clamp(voice_data.get("tone", 0.5)),
                    cadence=self._clamp(voice_data.get("cadence", 0.5)),
                    warmth=self._clamp(voice_data.get("warmth", 0.5)),
                    solemnity=self._clamp(voice_data.get("solemnity", 0.5)),
                    gender=gender,
                    age_hint=voice_data.get("age_hint", "adult"),
                    accent_hint=voice_data.get("accent_hint"),
                    dialogue_text=voice_data.get("dialogue_text"),
                    voice_notes=voice_data.get("voice_notes")
                )
                voice_directions.append(direction)
                
            except Exception as e:
                print(f"Warning: Failed to parse voice direction: {e}")
                # Add a default silent direction
                voice_directions.append(VoiceDirection())
        
        return voice_directions
    
    def _format_scenes_description(self, scenes: List[SceneStep]) -> str:
        """Format scenes into description for the prompt"""
        lines = []
        
        for scene in sorted(scenes, key=lambda s: s.scene_number):
            lines.append(f"""
Scene {scene.scene_number}:
  - Time: {scene.time_start:.1f}s to {scene.time_end:.1f}s (duration: {scene.duration:.1f}s)
  - Description: {scene.description}
  - Mood: {scene.mood}
  - Audio Context: {scene.audio_context}
  - Visual: {scene.visual_prompt_draft[:100]}...
""")
        
        return "\n".join(lines)
    
    def _clamp(self, value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Clamp a value to the specified range"""
        try:
            return max(min_val, min(max_val, float(value)))
        except (TypeError, ValueError):
            return 0.5
    
    async def analyze_single_scene(
        self,
        scene: SceneStep,
        project_script: str,
        context_scenes: Optional[List[SceneStep]] = None
    ) -> VoiceDirection:
        """
        Analyze a single scene for voice direction.
        Useful for re-analyzing specific scenes.
        
        Args:
            scene: The scene to analyze
            project_script: User's creative vision
            context_scenes: Surrounding scenes for context
        
        Returns:
            VoiceDirection for the scene
        """
        # Create a mini-plan with just this scene
        from .models import MasterPlan
        
        scenes = [scene]
        if context_scenes:
            scenes = context_scenes + [scene]
        
        mini_plan = MasterPlan(
            project_name="Single Scene Analysis",
            total_duration=scene.time_end,
            scenes=scenes
        )
        
        directions = await self.generate_voice_plan(mini_plan, project_script)
        
        # Return the direction for our target scene
        if directions:
            return directions[-1]  # Last one is our target scene
        
        return VoiceDirection()
