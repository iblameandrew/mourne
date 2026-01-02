from typing import Protocol, Any, Dict, Optional

class TextBackend(Protocol):
    async def generate_text(self, prompt: str, system: Optional[str] = None) -> str: ...

class SpeechBackend(Protocol):
    async def generate_speech(self, text: str, output_path: str) -> str: ...

class LocalTextBackend:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name
        # TODO: Initialize Ollama client
    
    async def generate_text(self, prompt: str, system: Optional[str] = None) -> str:
        # Placeholder for Ollama API call
        return f"[Ollama {self.model_name}] Response to: {prompt}"

class LocalSpeechBackend:
    def __init__(self, model_path="microsoft/speecht5_tts"):
        self.model_path = model_path
        # Placeholder for lazy loading HuggingFace pipeline
        self.pipeline = None
    
    async def generate_speech(self, text: str, output_path: str) -> str:
        """
        Generates speech using HuggingFace SafeTensors model.
        """
        import torch
        from transformers import pipeline
        from datasets import load_dataset
        import soundfile as sf
        
        if not self.pipeline:
            # We enforce SafeTensors usage via transformers
            print(f"Loading HF TTS Model from {self.model_path} (SafeTensors)...")
            self.pipeline = pipeline("text-to-speech", model=self.model_path, device="cuda" if torch.cuda.is_available() else "cpu")

        # Generate audio
        # Note: This is a simplifed example using speecht5_tts which might need speaker embeddings
        # For generic usage, we'd handle different architectures or assume a standard interface
        speech = self.pipeline(text)
        
        # Save to disk
        sf.write(output_path, speech["audio"], samplerate=speech["sampling_rate"])
        return output_path

class GoogleGeminiTTSBackend:
    def __init__(self, api_key: str, model_name="gemini-2.5-flash-preview-tts"):
        from google import genai
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key) if api_key else None
        
    async def generate_speech(self, text: str, output_path: str) -> str:
        from google.genai import types
        import wave
        
        if not self.client:
            raise ValueError("Google GenAI API Key not configured")

        # Simplified prompt structure for single speaker based on user input
        # In a real scenario, we might parse formatting for multi-speaker
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name='Kore', # Defaulting to Kore as per snippet example for 'Joe'
                        )
                    )
                )
            )
        )
        
        # Extract audio data
        # data = response.candidates[0].content.parts[0].inline_data.data
        # The snippet says: data = response.candidates[0].content.parts[0].inline_data.data
        # We need to decode it if it's base64, but the SDK 'inline_data.data' usually returns bytes directly
        # or we might need to handle it carefully.
        # However, likely 'inline_data.data' is bytes.
        
        data = response.candidates[0].content.parts[0].inline_data.data
        
        # Save to wave file (using the snippet's logic)
        with wave.open(output_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(data)
            
        return output_path

class BackendManager:
    def __init__(self):
        self.text_backend = LocalTextBackend()
        self.speech_backend = LocalSpeechBackend()
        
    def get_text_backend(self) -> TextBackend:
        return self.text_backend

    def get_speech_backend(self) -> SpeechBackend:
        return self.speech_backend
