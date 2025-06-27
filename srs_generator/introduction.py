import os
import requests
from .rag import AgentBase
from .first_page import SRSConcrete
from loguru import logger
from dotenv import load_dotenv

class IntroductionAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="IntroductionAgent", max_retries=max_retries, verbose=verbose)
        self.srs = SRSConcrete("SRSWriter", max_retries, verbose)
        load_dotenv()
        self.logger = logger

    def call_gemini(self, prompt, temperature=0.3, max_tokens=1024):
        """Call Gemini API to generate content"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            json_response = response.json()
            text = json_response['candidates'][0]['content']['parts'][0]['text']
            return text
        except Exception as e:
            self.logger.error(f"[{self.name}] Gemini API call failed: {str(e)}")
            return None

    def execute(self, topic):
        # Construct the prompt by combining system and user messages
        system_message = """You are an expert system requirement specification document writer who will write a good introduction of a provided description
        which includes
        1.1 Purpose: State the purpose of the SRS document, including the intended audience.
        1.2 Scope: Describe the system's features, objectives, and benefits.
        1.3 Definitions, Acronyms, and Abbreviations: Define key terms, acronyms, and abbreviations used.
        1.4 Document Conventions: Specify formatting rules and numbering schemes.
        1.5 Intended Audience and Reading Suggestions: Specify who should read the document and in what order.
        """
        
        user_message = (
            "please write the introduction for SRS docs of the following description : \n\n"
            f"{topic}\n\n here is the description:"
        )

        # Combine system and user messages into a single prompt
        full_prompt = f"{system_message}\n\n{user_message}"

        # Get introduction content from Gemini
        intro_content = None
        for attempt in range(self.max_retries):
            intro_content = self.call_gemini(full_prompt, temperature=0.3, max_tokens=1024)
            if intro_content:
                break
            self.logger.warning(f"[{self.name}] Attempt {attempt + 1} failed to generate introduction content")
        
        if not intro_content:
            self.logger.error(f"[{self.name}] Failed to generate introduction content after all retries")
            intro_content = "Failed to generate introduction content."

        return intro_content