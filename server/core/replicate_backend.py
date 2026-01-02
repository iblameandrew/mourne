"""
Replicate media backend for Mourne.
Provides image and video generation via Replicate API.
"""
import os
import asyncio
import httpx
from typing import Optional


class ReplicateImageBackend:
    """
    Generates images using Replicate API (e.g., SDXL, Flux).
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "stability-ai/sdxl"):
        self._api_key = api_key
        self.model = model
        self.base_url = "https://api.replicate.com/v1"
    
    @property
    def api_key(self) -> str:
        key = self._api_key or os.environ.get("REPLICATE_API_TOKEN")
        if not key:
            raise ValueError("REPLICATE_API_TOKEN environment variable not set")
        return key
    
    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_image(
        self, 
        prompt: str, 
        output_path: str,
        width: int = 1024,
        height: int = 1024,
        negative_prompt: Optional[str] = None
    ) -> str:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Text description of the image
            output_path: Path to save the image (extension will be added)
            width: Image width
            height: Image height
            negative_prompt: Things to avoid
        
        Returns:
            Path to the saved image
        """
        input_data = {
            "prompt": prompt,
            "width": width,
            "height": height
        }
        if negative_prompt:
            input_data["negative_prompt"] = negative_prompt
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            # Start prediction
            response = await client.post(
                f"{self.base_url}/predictions",
                headers=self._get_headers(),
                json={
                    "version": await self._get_model_version(client),
                    "input": input_data
                }
            )
            response.raise_for_status()
            prediction = response.json()
            
            # Poll for completion
            prediction_url = prediction["urls"]["get"]
            while prediction["status"] not in ["succeeded", "failed", "canceled"]:
                await asyncio.sleep(2)
                response = await client.get(prediction_url, headers=self._get_headers())
                response.raise_for_status()
                prediction = response.json()
            
            if prediction["status"] != "succeeded":
                raise RuntimeError(f"Image generation failed: {prediction.get('error')}")
            
            # Download the image
            output_url = prediction["output"]
            if isinstance(output_url, list):
                output_url = output_url[0]
            
            img_response = await client.get(output_url)
            img_response.raise_for_status()
            
            full_path = f"{output_path}.png"
            with open(full_path, "wb") as f:
                f.write(img_response.content)
            
            return full_path
    
    async def _get_model_version(self, client: httpx.AsyncClient) -> str:
        """Get the latest version of the model"""
        response = await client.get(
            f"{self.base_url}/models/{self.model}/versions",
            headers=self._get_headers()
        )
        response.raise_for_status()
        versions = response.json()["results"]
        return versions[0]["id"]


class ReplicateVideoBackend:
    """
    Generates videos using Replicate API (e.g., Stable Video Diffusion).
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "stability-ai/stable-video-diffusion"):
        self._api_key = api_key
        self.model = model
        self.base_url = "https://api.replicate.com/v1"
    
    @property
    def api_key(self) -> str:
        key = self._api_key or os.environ.get("REPLICATE_API_TOKEN")
        if not key:
            raise ValueError("REPLICATE_API_TOKEN environment variable not set")
        return key
    
    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_video(
        self, 
        prompt: str, 
        output_path: str,
        input_image_path: Optional[str] = None,
        duration_seconds: int = 4,
        fps: int = 24,
        width: int = 1024,
        height: int = 576
    ) -> str:
        """
        Generate a video from a text prompt or an image.
        
        Args:
            prompt: Text description of the video
            output_path: Path to save the video (.mp4)
            input_image_path: Optional path to an image to animate
            duration_seconds: Video duration
            fps: Frames per second
            width: Video width
            height: Video height
        
        Returns:
            Path to the saved video
        """
        input_data = {
            "prompt": prompt,
            "video_length": duration_seconds * fps,
            "width": width,
            "height": height,
            "fps": fps
        }
        
        if input_image_path and os.path.exists(input_image_path):
            # For Replicate via HTTP, we usually need to upload the file first
            # to get a URL, or use a data URI for small files.
            # Stable Video Diffusion on Replicate specifically uses 'input_image'
            import base64
            with open(input_image_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                mime_type = mimetypes.guess_type(input_image_path)[0] or "image/png"
                input_data["input_image"] = f"data:{mime_type};base64,{encoded}"

        async with httpx.AsyncClient(timeout=600.0) as client:
            # Start prediction
            response = await client.post(
                f"{self.base_url}/predictions",
                headers=self._get_headers(),
                json={
                    "version": await self._get_model_version(client),
                    "input": input_data
                }
            )
            response.raise_for_status()
            prediction = response.json()
            
            # Poll for completion
            prediction_url = prediction["urls"]["get"]
            while prediction["status"] not in ["succeeded", "failed", "canceled"]:
                await asyncio.sleep(5)
                response = await client.get(prediction_url, headers=self._get_headers())
                response.raise_for_status()
                prediction = response.json()
            
            if prediction["status"] != "succeeded":
                raise RuntimeError(f"Video generation failed: {prediction.get('error')}")
            
            # Download the video
            output_url = prediction["output"]
            if isinstance(output_url, list):
                output_url = output_url[0]
            
            vid_response = await client.get(output_url)
            vid_response.raise_for_status()
            
            with open(output_path, "wb") as f:
                f.write(vid_response.content)
            
            return output_path
    
    async def _get_model_version(self, client: httpx.AsyncClient) -> str:
        """Get the latest version of the model"""
        response = await client.get(
            f"{self.base_url}/models/{self.model}/versions",
            headers=self._get_headers()
        )
        response.raise_for_status()
        versions = response.json()["results"]
        return versions[0]["id"]
