"""
Runway ML Video Backend for Mourne.
Generates videos using Runway ML's image-to-video API.
"""
import os
import time
import asyncio
import httpx
from typing import Optional


class RunwayVideoBackend:
    """
    Generates videos using Runway ML's Gen-4 Turbo model.
    Handles image-to-video generation with polling for completion.
    """
    
    BASE_URL = "https://api.runwayml.com/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.environ.get("RUNWAY_API_KEY")
        self.model = "gen4_turbo"
        self.default_ratio = "1280:720"
        self.default_duration = 4
    
    @property
    def headers(self):
        """Get authorization headers"""
        if not self._api_key:
            raise ValueError("RUNWAY_API_KEY not set")
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06"
        }
    
    async def generate_video(
        self,
        prompt: str,
        output_path: str,
        input_image_path: Optional[str] = None,
        input_image_url: Optional[str] = None,
        duration_seconds: int = 4,
        ratio: str = "1280:720",
        seed: Optional[int] = None,
        poll_interval: int = 10
    ) -> str:
        """
        Generate a video from an image using Runway ML.
        
        Args:
            prompt: Text description of the motion/action
            output_path: Full path for output video file (.mp4)
            input_image_path: Local path to input image (will be uploaded)
            input_image_url: URL to input image (alternative to path)
            duration_seconds: Video duration (4, 5, or 10 seconds)
            ratio: Aspect ratio ("1280:720", "720:1280", "1024:1024")
            seed: Optional seed for reproducibility
            poll_interval: Seconds between status checks
        
        Returns:
            Path to the saved video file
        """
        # Prepare image input
        if input_image_path and os.path.exists(input_image_path):
            # For local images, we need to either upload or use base64
            # For now, we'll require a URL or use a placeholder
            import base64
            with open(input_image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            image_uri = f"data:image/jpeg;base64,{image_data}"
        elif input_image_url:
            image_uri = input_image_url
        else:
            raise ValueError("Either input_image_path or input_image_url is required")
        
        # Build request payload
        payload = {
            "promptText": prompt,
            "promptImage": [
                {
                    "uri": image_uri,
                    "position": "first"
                }
            ],
            "model": self.model,
            "ratio": ratio,
            "duration": duration_seconds
        }
        
        if seed is not None:
            payload["seed"] = seed
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            # Start the generation task
            print(f"Starting Runway video generation...")
            response = await client.post(
                f"{self.BASE_URL}/image_to_video",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            task_data = response.json()
            task_id = task_data.get("id")
            
            if not task_id:
                raise RuntimeError(f"No task ID returned: {task_data}")
            
            print(f"Task started: {task_id}")
            
            # Poll for completion
            while True:
                await asyncio.sleep(poll_interval)
                
                status_response = await client.get(
                    f"{self.BASE_URL}/tasks/{task_id}",
                    headers=self.headers
                )
                status_response.raise_for_status()
                status_data = status_response.json()
                
                status = status_data.get("status")
                print(f"Task status: {status}")
                
                if status == "SUCCEEDED":
                    # Get the output URL
                    output_url = status_data.get("output", [None])[0]
                    if not output_url:
                        raise RuntimeError("Task succeeded but no output URL")
                    
                    # Download the video
                    print(f"Downloading video from: {output_url}")
                    video_response = await client.get(output_url)
                    video_response.raise_for_status()
                    
                    with open(output_path, "wb") as f:
                        f.write(video_response.content)
                    
                    print(f"Video saved to: {output_path}")
                    return output_path
                
                elif status == "FAILED":
                    error = status_data.get("error", "Unknown error")
                    raise RuntimeError(f"Runway task failed: {error}")
                
                elif status in ["PENDING", "RUNNING"]:
                    continue
                
                else:
                    print(f"Unknown status: {status}, continuing to poll...")
