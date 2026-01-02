"""
OpenRouter LLM Backend for Mourne.
Provides a unified interface to various LLM providers via OpenRouter.
"""
import os
import json
import httpx
from typing import Optional, Dict, Any, List


class OpenRouterLLM:
    """
    Cloud LLM via OpenRouter - supports any model available on the platform.
    
    Default model: anthropic/claude-3.5-sonnet
    Alternative models: openai/gpt-4o, google/gemini-pro, meta-llama/llama-3-70b-instruct
    """
    
    def __init__(
        self, 
        model: str = "anthropic/claude-3.5-sonnet",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = model
        self._api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @property
    def api_key(self) -> str:
        """Get API key, checking environment if not provided"""
        key = self._api_key or os.environ.get("OPENROUTER_API_KEY")
        if not key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        return key
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://mourne.app",  # Optional: for rankings
            "X-Title": "Mourne Video Generator"     # Optional: for rankings
        }
    
    async def generate(
        self, 
        prompt: str, 
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate text completion from the LLM.
        
        Args:
            prompt: The user prompt
            system: Optional system message
            temperature: Override default temperature
            max_tokens: Override default max tokens
            response_format: Optional response format (e.g., {"type": "json_object"})
        
        Returns:
            Generated text response
        """
        messages: List[Dict[str, str]] = []
        
        if system:
            messages.append({"role": "system", "content": system})
        
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }
        
        if response_format:
            payload["response_format"] = response_format
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def generate_json(
        self, 
        prompt: str, 
        system: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate a JSON response from the LLM.
        
        Args:
            prompt: The user prompt (should request JSON output)
            system: Optional system message
            temperature: Override default temperature
        
        Returns:
            Parsed JSON dictionary
        """
        # Add JSON instruction to system message
        json_system = (system or "") + "\n\nRespond with valid JSON only. No markdown, no explanation."
        
        response = await self.generate(
            prompt=prompt,
            system=json_system.strip(),
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        
        # Parse JSON response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response if wrapped in markdown
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
            if json_match:
                return json.loads(json_match.group(1))
            raise ValueError(f"Failed to parse JSON response: {response[:500]}")
    
    def with_model(self, model: str) -> "OpenRouterLLM":
        """Create a new instance with a different model"""
        return OpenRouterLLM(
            model=model,
            api_key=self._api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
    
    def with_temperature(self, temperature: float) -> "OpenRouterLLM":
        """Create a new instance with different temperature"""
        return OpenRouterLLM(
            model=self.model,
            api_key=self._api_key,
            temperature=temperature,
            max_tokens=self.max_tokens
        )


# Convenience factory functions
def get_planner_llm() -> OpenRouterLLM:
    """Get an LLM optimized for planning tasks (lower temperature)"""
    return OpenRouterLLM(
        model=os.environ.get("PLANNER_MODEL", "anthropic/claude-3.5-sonnet"),
        temperature=0.5
    )


def get_creative_llm() -> OpenRouterLLM:
    """Get an LLM optimized for creative tasks (higher temperature)"""
    return OpenRouterLLM(
        model=os.environ.get("CREATIVE_MODEL", "anthropic/claude-3.5-sonnet"),
        temperature=0.9
    )


def get_code_llm() -> OpenRouterLLM:
    """Get an LLM optimized for code generation"""
    return OpenRouterLLM(
        model=os.environ.get("CODE_MODEL", "anthropic/claude-3.5-sonnet"),
        temperature=0.3,
        max_tokens=8192
    )
