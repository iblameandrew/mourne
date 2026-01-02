"""
Media generation backends for Mourne.
Provides image generation via Google Gemini and video generation via Veo.
"""
import os
import time
import mimetypes
import asyncio
from typing import Optional
from google import genai
from google.genai import types


class GeminiImageBackend:
    """
    Generates images using Google Gemini 3 Pro Image Preview.
    Based on the google-genai SDK.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key
        self._client = None
        self.model = "gemini-3-pro-image-preview"
    
    @property
    def client(self):
        """Lazy initialization of the Gemini client"""
        if self._client is None:
            api_key = self._api_key or os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
            self._client = genai.Client(api_key=api_key)
        return self._client
    
    async def generate_image(
        self, 
        prompt: str, 
        output_path: str,
        image_size: str = "1K"
    ) -> str:
        """
        Generate an image from a text prompt and save to disk.
        
        Args:
            prompt: Text description of the image to generate
            output_path: Base path for output (extension will be added)
            image_size: Image size ("1K" or "2K")
        
        Returns:
            Full path to the saved image file
        """
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        
        # Optional: Enable Google Search for reference (can improve quality)
        tools = [
            types.Tool(googleSearch=types.GoogleSearch()),
        ]
        
        config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            image_config=types.ImageConfig(image_size=image_size),
            tools=tools,
        )
        
        # Run synchronous streaming in executor to not block
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            self._generate_sync, 
            contents, 
            config, 
            output_path
        )
        
        return result
    
    def _generate_sync(
        self, 
        contents: list, 
        config: types.GenerateContentConfig,
        output_path: str
    ) -> str:
        """Synchronous generation (called in executor)"""
        
        file_index = 0
        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=config,
        ):
            if (
                chunk.candidates is None
                or chunk.candidates[0].content is None
                or chunk.candidates[0].content.parts is None
            ):
                continue
            
            part = chunk.candidates[0].content.parts[0]
            if part.inline_data and part.inline_data.data:
                inline_data = part.inline_data
                file_extension = mimetypes.guess_extension(inline_data.mime_type) or ".png"
                
                # Add index if multiple images
                if file_index > 0:
                    full_path = f"{output_path}_{file_index}{file_extension}"
                else:
                    full_path = f"{output_path}{file_extension}"
                
                with open(full_path, "wb") as f:
                    f.write(inline_data.data)
                
                print(f"Image saved to: {full_path}")
                file_index += 1
                
                # Return first image path
                if file_index == 1:
                    return full_path
        
        raise RuntimeError("No image data received from Gemini API")


class VeoVideoBackend:
    """
    Generates videos using Google Veo 3.1.
    Handles the long-running operation with polling.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key
        self._client = None
        self.model = "veo-3.1-generate-preview"
    
    @property
    def client(self):
        """Lazy initialization of the Gemini client"""
        if self._client is None:
            api_key = self._api_key or os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
            self._client = genai.Client(api_key=api_key)
        return self._client
    
    async def generate_video(
        self, 
        prompt: str, 
        output_path: str,
        input_image_path: Optional[str] = None,
        duration_seconds: int = 6,
        resolution: str = "1080p",
        aspect_ratio: str = "16:9",
        negative_prompt: Optional[str] = None,
        poll_interval: int = 15
    ) -> str:
        """
        Generate a video from a text prompt or an image.
        
        Args:
            prompt: Text description of the video to generate
            output_path: Full path for output video file (.mp4)
            input_image_path: Optional path to an image to animate (image-to-video)
            duration_seconds: Video duration (4, 6, or 8 seconds)
            resolution: "720p" or "1080p"
            aspect_ratio: "16:9" or "9:16"
            negative_prompt: Things to avoid in the video
            poll_interval: Seconds between status checks
        
        Returns:
            Path to the saved video file
        """
        # Run in executor to not block
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._generate_sync,
            prompt,
            output_path,
            input_image_path,
            duration_seconds,
            resolution,
            aspect_ratio,
            negative_prompt,
            poll_interval
        )
        
        return result
    
    def _generate_sync(
        self,
        prompt: str,
        output_path: str,
        input_image_path: Optional[str],
        duration_seconds: int,
        resolution: str,
        aspect_ratio: str,
        negative_prompt: Optional[str],
        poll_interval: int
    ) -> str:
        """Synchronous video generation with polling (called in executor)"""
        
        # Build config
        config_kwargs = {
            "resolution": resolution,
            "duration_seconds": duration_seconds,
            "aspect_ratio": aspect_ratio,
        }
        if negative_prompt:
            config_kwargs["negative_prompt"] = negative_prompt
        
        config = types.GenerateVideosConfig(**config_kwargs)
        
        # Build image input if provided
        kwargs = {
            "model": self.model,
            "prompt": prompt,
            "config": config,
        }
        
        if input_image_path and os.path.exists(input_image_path):
            # Load the image using the genai types
            print(f"Loading input image for animation: {input_image_path}")
            with open(input_image_path, "rb") as f:
                kwargs["image"] = types.Image.from_bytes(data=f.read())

        # Start long-running operation
        operation = self.client.models.generate_videos(**kwargs)
        
        print(f"Video generation started: {operation.name}")
        
        # Poll for completion
        while not operation.done:
            print(f"Waiting for video generation... (polling every {poll_interval}s)")
            time.sleep(poll_interval)
            operation = self.client.operations.get(operation)
        
        # Process result
        # The operation response contains the generated videos
        if operation.response and operation.response.generated_videos:
            generated_video = operation.response.generated_videos[0]
            print(f"Video generated: {generated_video.video.name}")
            
            # Download the video using the client.download method
            self.client.download(
                file=generated_video.video, 
                path=output_path
            )
            print(f"Video downloaded to: {output_path}")
            
            return output_path
        else:
            raise RuntimeError(f"Video generation failed or returned no result: {operation.error if hasattr(operation, 'error') else 'Unknown error'}")


class MediaBackendManager:
    """Factory for media backends - supports Google and Replicate providers"""
    
    _provider: str = "google"  # 'google' | 'replicate'
    _image_backend = None
    _video_backend = None
    
    @classmethod
    def set_provider(cls, provider: str):
        """Set the active provider and reset backends"""
        if provider not in ["google", "replicate"]:
            raise ValueError(f"Unknown provider: {provider}")
        if provider != cls._provider:
            cls._provider = provider
            cls._image_backend = None
            cls._video_backend = None
    
    @classmethod
    def get_provider(cls) -> str:
        return cls._provider
    
    @classmethod
    def get_image_backend(cls):
        """Get image backend for current provider"""
        if cls._image_backend is None:
            if cls._provider == "google":
                cls._image_backend = GeminiImageBackend()
            else:
                from .replicate_backend import ReplicateImageBackend
                cls._image_backend = ReplicateImageBackend()
        return cls._image_backend
    
    @classmethod
    def get_video_backend(cls):
        """Get video backend for current provider"""
        if cls._video_backend is None:
            if cls._provider == "google":
                cls._video_backend = VeoVideoBackend()
            else:
                from .replicate_backend import ReplicateVideoBackend
                cls._video_backend = ReplicateVideoBackend()
        return cls._video_backend

