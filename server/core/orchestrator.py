import json
import asyncio
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import (
    RunnablePassthrough, 
    RunnableParallel, 
    RunnableLambda, 
    RunnableBranch,
    ConfigurableField
)
from langchain_core.documents.base import Blob
from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser

class Orchestrator:
    """
    Async Orchestrator for the Web Backend.
    """
    def __init__(self, model_name="gpt-4o"):
        self.model_name = model_name
        self.primary_llm = ChatOpenAI(model=model_name).configurable_fields(
            temperature=ConfigurableField(id="temp")
        )
        self.fallback_llm = ChatOpenAI(model="gpt-3.5-turbo")
        self.llm = self.primary_llm.with_fallbacks([self.fallback_llm])
        
        # Setup Chain
        self._setup_chain()

    async def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribes audio using OpenAI Whisper (via LangChain Parser).
        """
        # The audio file path is wrapped in a Blob object
        audio_blob = Blob(path=audio_path)

        parser = OpenAIWhisperParser()
        # lazy_parse returns an iterator, we iterate to get documents
        documents = list(parser.lazy_parse(blob=audio_blob)) 
        
        # Combine content from all documents (usually just one for a file)
        transcription = "\n".join([doc.page_content for doc in documents])
        print(f"Transcription Result: {transcription[:100]}...")
        return transcription
        
    def _setup_chain(self):
        # 2. --- THE SUB-CHAINS ---
        # Researcher Node
        research_prompt = ChatPromptTemplate.from_template("Analyze this video script/concept: {topic}. Break it down into visual motifs and mood. Summary:")
        researcher = research_prompt | self.llm | StrOutputParser()

        # Critic Node
        critic_prompt = ChatPromptTemplate.from_template(
            "Rate this analysis as 'PASS' or 'FAIL'. Report: {report}. Logic: Provide JSON with 'rating' and 'reason'."
        )
        critic = critic_prompt | self.llm | JsonOutputParser()

        # 3. --- THE RECURSIVE LOOP LOGIC ---
        def self_correcting_loop(state: Dict[str, Any]) -> Dict[str, Any]:
            """The 'Brain' of the loop that decides to recurse or exit."""
            count = state.get('count', 1)
            # In a real async flow, we might stream logs here via a callback handler
            print(f"--- Iteration {count} ---")
            
            # Run the critic on the current report
            critique = critic.invoke({"report": state["report"]})
            
            # EXIT CONDITION: Pass or Max Retries
            if critique["rating"] == "PASS" or count >= state["max_retries"]:
                return {**state, "final_status": "Complete", "critique": critique}
            
            # RECURSE: Rewrite and call self again
            rewrite_prompt = ChatPromptTemplate.from_template(
                "Improve this report based on: {reason}. Original: {report}"
            )
            new_report = (rewrite_prompt | self.llm | StrOutputParser()).invoke({
                "reason": critique["reason"], 
                "report": state["report"]
            })
            
            # Logic for the next 'Turn'
            next_state = {
                **state,
                "report": new_report,
                "count": count + 1
            }
            return self_correcting_loop(next_state)

        # 4. --- THE MEGA CHAIN ASSEMBLY ---
        self.chain = (
            # STEP A: Initialize State in Parallel
            RunnableParallel({
                "topic": RunnablePassthrough(),
                "report": researcher, # Kick off the first draft
                "count": lambda x: 1,
                "max_retries": lambda x: 3
            })
            # STEP B: Enter the Recursive Lambda
            | RunnableLambda(self_correcting_loop)
            # STEP C: Final Formatting Branch
            | RunnableBranch(
                (lambda x: x["count"] > 2, ChatPromptTemplate.from_template("Summarize this (it took too long): {report}") | self.llm),
                (lambda x: True, RunnableLambda(lambda x: x["report"]))
            )
            | StrOutputParser()
        )

    async def run_analysis(self, topic: str):
        """
        Runs the orchestration chain asynchronously.
        """
        config = {"configurable": {"temp": 0.7}}
        # LangChain's invoke is synchronous, for async we use ainvoke
        result = await self.chain.ainvoke(topic, config=config)
        return result
