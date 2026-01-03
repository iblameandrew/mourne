"""
Style Analyzer for Mourne.
Analyzes reference images to extract style descriptors for consistent media generation.
"""
import os
import base64
import asyncio
from typing import Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types


class StyleReference(BaseModel):
    """Extracted style descriptors from a reference image"""
    
    # Core style elements
    artistic_style: str = Field(description="e.g., photorealistic, anime, oil painting, watercolor")
    rendering_technique: str = Field(description="e.g., cel-shaded, hyperrealistic, impressionistic")
    
    # Visual characteristics
    color_palette: str = Field(description="Dominant colors and color harmony type")
    lighting_style: str = Field(description="e.g., golden hour, neon, dramatic chiaroscuro")
    texture_quality: str = Field(description="e.g., smooth, grainy, painterly brushstrokes")
    
    # Mood and atmosphere
    mood: str = Field(description="Emotional tone conveyed by the image")
    atmosphere: str = Field(description="e.g., foggy, crisp, dreamlike, gritty")
    
    # Technical aspects
    composition_notes: str = Field(description="Notable composition techniques")
    detail_level: str = Field(description="e.g., highly detailed, minimalist, stylized")
    
    # The combined style prompt to inject
    style_prompt: str = Field(description="A concise style directive to append to prompts")
    
    # Source
    source_image_path: Optional[str] = None


STYLE_ANALYZER_PROMPT = """Analyze this reference image and extract comprehensive style descriptors.

Your analysis will be used to maintain visual consistency across AI-generated media assets.

Provide your analysis in the following JSON format:
{
    "artistic_style": "The overall artistic style (e.g., photorealistic, anime, oil painting, watercolor, digital illustration)",
    "rendering_technique": "How the image appears to be rendered (e.g., cel-shaded, hyperrealistic, impressionistic, flat design)",
    "color_palette": "Dominant colors and color harmony (e.g., warm earth tones with amber and sienna, cool blues with teal accents)",
    "lighting_style": "The lighting approach (e.g., soft diffused daylight, dramatic rim lighting, neon glow, golden hour warmth)",
    "texture_quality": "Texture characteristics (e.g., smooth gradients, visible brushstrokes, film grain, clean vectors)",
    "mood": "The emotional tone (e.g., serene and contemplative, energetic and vibrant, melancholic and nostalgic)",
    "atmosphere": "Environmental atmosphere (e.g., misty and ethereal, crisp and clear, hazy and dreamlike)",
    "composition_notes": "Notable composition elements (e.g., rule of thirds, centered symmetry, dynamic diagonals)",
    "detail_level": "Level of detail (e.g., highly intricate with fine details, stylized with bold shapes, minimalist)",
    "style_prompt": "A concise 1-2 sentence style directive that can be appended to any prompt to achieve this look. Example: 'In the style of Studio Ghibli, with soft watercolor textures, warm pastel colors, and gentle diffused lighting.'"
}

Return ONLY valid JSON. No explanation, no markdown."""


class StyleAnalyzer:
    """
    Analyzes reference images to extract visual style descriptors.
    Uses Google's Gemini vision model for image understanding.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self._client = None
        self.model = "gemini-2.5-flash"
    
    @property
    def client(self):
        """Lazy initialization of the Gemini client"""
        if self._client is None:
            if not self._api_key:
                raise ValueError("GEMINI_API_KEY not set")
            self._client = genai.Client(api_key=self._api_key)
        return self._client
    
    async def analyze(self, image_path: str) -> StyleReference:
        """
        Analyze an image and extract style descriptors.
        
        Args:
            image_path: Path to the reference image
        
        Returns:
            StyleReference with extracted style information
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        # Determine mime type
        ext = os.path.splitext(image_path)[1].lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        mime_type = mime_types.get(ext, "image/jpeg")
        
        # Run analysis in executor
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._analyze_sync,
            image_data,
            mime_type,
            image_path
        )
        
        return result
    
    def _analyze_sync(
        self, 
        image_data: bytes, 
        mime_type: str,
        image_path: str
    ) -> StyleReference:
        """Synchronous analysis (called in executor)"""
        
        # Create content with image
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(data=image_data, mime_type=mime_type),
                    types.Part.from_text(text=STYLE_ANALYZER_PROMPT)
                ]
            )
        ]
        
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3
        )
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config
        )
        
        # Parse JSON response
        import json
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            text = response.text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(text[start:end])
            else:
                raise ValueError(f"Failed to parse style analysis: {text}")
        
        return StyleReference(
            artistic_style=data.get("artistic_style", "photorealistic"),
            rendering_technique=data.get("rendering_technique", "cinematic"),
            color_palette=data.get("color_palette", "natural colors"),
            lighting_style=data.get("lighting_style", "natural lighting"),
            texture_quality=data.get("texture_quality", "detailed"),
            mood=data.get("mood", "neutral"),
            atmosphere=data.get("atmosphere", "clear"),
            composition_notes=data.get("composition_notes", "balanced"),
            detail_level=data.get("detail_level", "moderate detail"),
            style_prompt=data.get("style_prompt", ""),
            source_image_path=image_path
        )
