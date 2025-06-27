import os
import requests
from .rag import AgentBase
from .first_page import SRSConcrete
from loguru import logger
from dotenv import load_dotenv

class SystemFeaturesAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="SystemFeaturesAgent", max_retries=max_retries, verbose=verbose)
        self.srs = SRSConcrete("SRSWriter", max_retries, verbose)
        load_dotenv()
        self.logger = logger

    def call_gemini(self, prompt, temperature=0.3, max_tokens=2000):
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
            self.logger.error(f"Gemini API call failed: {str(e)}")
            return None

    def execute(self, topic, previous_contents):
        # Construct the prompt by combining system and user messages
        system_message = """You are an expert system requirement specification document writer. Based on the introduction and overall description provided, write a detailed system features section.

        For each major feature mentioned in the previous sections, provide:

        3.x Feature Name: (Meaningful name of the feature)
        Description: Detailed overview of what the feature does
        Input: Required data inputs for this feature
        Output: Expected outputs or results
        Priority: Importance level (High, Medium, Low)
        Functional Requirements: Detailed requirements numbered as FR 3.x.1, FR 3.x.2, etc.

        Format each feature consistently using the structure above.
        Ensure features align with the product functions mentioned in the overall description.
        Number features as 3.1, 3.2, etc.
        """
        
        user_message = (
            f"Here is the project description:\n{topic}\n\n"
            f"Here is the introduction:\n{previous_contents['introduction']}\n\n"
            f"Here is the overall description:\n{previous_contents['overall_description']}\n\n"
            "Please write the System Features section that aligns with these previous sections:"
        )

        # Combine system and user messages into a single prompt
        full_prompt = f"{system_message}\n\n{user_message}"

        # Get system features content from Gemini
        features_content = None
        for attempt in range(self.max_retries):
            features_content = self.call_gemini(full_prompt, temperature=0.3, max_tokens=2000)
            if features_content:
                break
            self.logger.warning(f"Attempt {attempt + 1} failed to generate system features content")
        
        if not features_content:
            self.logger.error("Failed to generate system features content after all retries")
            features_content = "Failed to generate system features content."

        # Return all contents for use in next sections
        return {
            "introduction": previous_contents["introduction"],
            "overall_description": previous_contents["overall_description"],
            "system_features": features_content
        }