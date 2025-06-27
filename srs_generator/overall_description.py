import os
import requests
from .rag import AgentBase
from .first_page import SRSConcrete
from loguru import logger
from dotenv import load_dotenv

class OverallDescriptionAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="OverallDescriptionAgent", max_retries=max_retries, verbose=verbose)
        self.srs = SRSConcrete("SRSWriter", max_retries, verbose)
        load_dotenv()
        self.logger = logger

    def call_gemini(self, prompt, temperature=0.3, max_tokens=1500):
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

    def execute(self, topic, intro_content):
        # Construct the prompt by combining system and user messages
        system_message = """You are an expert system requirement specification document writer. Based on the introduction provided, write a comprehensive overall description section that includes:

        2.1 Product Perspective: Describe the product's context, including system interfaces and dependencies.
        2.2 Product Functions: High-level overview of the system's major functionalities.
        2.3 User Classes and Characteristics: Identify the types of users (e.g., Admin, Regular User).
        2.4 Operating Environment: Specify hardware, software, and network requirements.
        2.5 Design and Implementation Constraints: Highlight limitations like technology choices or legal constraints.
        2.6 Assumptions and Dependencies: Assumptions that may impact requirements.

        Keep your response consistent with the introduction provided.
        """
        
        user_message = (
            f"Here is the project description:\n{topic}\n\n"
            f"And here is the introduction already written:\n{intro_content}\n\n"
            "Please write the Overall Description section that aligns with this introduction:"
        )

        # Combine system and user messages into a single prompt
        full_prompt = f"{system_message}\n\n{user_message}"

        # Get overall description content from Gemini
        overall_desc_content = None
        for attempt in range(self.max_retries):
            overall_desc_content = self.call_gemini(full_prompt, temperature=0.3, max_tokens=1500)
            if overall_desc_content:
                break
            self.logger.warning(f"[{self.name}] Attempt {attempt + 1} failed to generate overall description content")
        
        if not overall_desc_content:
            self.logger.error(f"[{self.name}] Failed to generate overall description content after all retries")
            overall_desc_content = "Failed to generate overall description content."

        # Return both contents for use in next sections
        return {
            "introduction": intro_content,
            "overall_description": overall_desc_content
        }