from typing import List, Optional
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents.base import Blob
from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser

@dataclass
class StitchingCard:
    id: str
    time_start: float
    time_end: float
    visual_prompt: str
    audio_cue: str
    mood_description: str
    asset_path: Optional[str] = None
    media_type: str = "video"

@dataclass
class VideoProject:
    name: str
    script: str
    song_path: str
    cards: List[StitchingCard]

class Director:
    """
    The 'Master Director' that takes a project plan (assets, timing, mood)
    and generates the final Python script to stitch them together using MoviePy.
    """
    def __init__(self, model_name="gpt-4o"):
        self.llm = ChatOpenAI(model=model_name)
        
    async def analyze_song_lyrics(self, song_path: str) -> str:
        """
        Transcribes the song lyrics/audio to inform the video pacing and content.
        """
        # The audio file path is wrapped in a Blob object
        audio_blob = Blob(path=song_path)

        parser = OpenAIWhisperParser()
        # lazy_parse returns an iterator, we iterate to get documents
        documents = list(parser.lazy_parse(blob=audio_blob)) 
        
        # Combine content
        transcription = "\n".join([doc.page_content for doc in documents])
        print(f"Director Audio Analysis: {transcription[:100]}...")
        return transcription
        
    async def generate_stitching_script(self, project: VideoProject) -> str:
        """
        Generates a Python script using MoviePy to assemble the video.
        """
        
        # Serialize cards for the prompt
        cards_desc = "\n".join([
            f"- Time {c.time_start}-{c.time_end}: {c.media_type} '{c.asset_path}' (Mood: {c.mood_description}, Audio: {c.audio_cue})"
            for c in project.cards
        ])
        
        prompt = ChatPromptTemplate.from_template("""
        You are an expert Video Editor and Python Programmer specialized in MoviePy.
        
        Goal: Create a complete, runnable Python script to stitch together a music video based on the following plan.
        
        Project: {project_name}
        Song Path: {song_path}
        
        Assets / Timeline:
        {cards_desc}
        
        Instructions:
        1. Use 'moviepy.editor' (or 'moviepy.v2' if appropriate).
        2. Load the specific image/video assets provided.
        3. Load the audio file.
        4. Implement the requested timing exactly.
        5. Apply simple crossfade transitions (0.5s).
        6. Apply "Ken Burns" effects to static images.
        7. The script must define a function `render_video(output_path)` that produces the file.
        8. RETURN ONLY THE CODE.
        
        Constraint: 
        - Assume all asset paths are relative to the 'server/static' directory or passed absolute.
        """)
        
        chain = prompt | self.llm | StrOutputParser()
        
        script_code = await chain.ainvoke({
            "project_name": project.name,
            "song_path": project.song_path,
            "cards_desc": cards_desc
        })
        
        return script_code
