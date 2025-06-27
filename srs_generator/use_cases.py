import os
import requests
from .rag import AgentBase
from .first_page import SRSConcrete
from loguru import logger
from dotenv import load_dotenv

class UseCasesAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="UseCasesAgent", max_retries=max_retries, verbose=verbose)
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
        system_message = """You are an expert system requirement specification document writer. Based on all previous sections provided, write a comprehensive Use Cases section that includes:

        6. Use Cases:
        - Detailed scenarios for each primary feature or interaction.
        - Include the following for each use case:

        6.1 Use Case Name (e.g., Real-Time Monitoring)
        6.1.1 Actors: Users or systems interacting with the feature.
        6.1.2 Description: Detailed scenario of the use case.
        6.1.3 Preconditions: Conditions that must be met before the use case.
        6.1.4 Postconditions: Expected state after the use case is executed.
        6.1.5 Main Flow: Primary sequence of steps.
        6.1.6 Alternate Flows: Variations or exceptions in the flow.
        
        Ensure alignment with previously defined features and requirements."""
        
        user_message = (
            f"Here is the project description:\n{topic}\n\n"
            f"Here is the introduction:\n{previous_contents['introduction']}\n\n"
            f"Here is the overall description:\n{previous_contents['overall_description']}\n\n"
            f"Here are the system features:\n{previous_contents['system_features']}\n\n"
            f"Here are the external interfaces:\n{previous_contents['external_interfaces']}\n\n"
            f"Here are the non-functional requirements:\n{previous_contents['non_functional_requirements']}\n\n"
            "Please write the Use Cases section that aligns with all previous sections:"
        )

        # Combine system and user messages into a single prompt
        full_prompt = f"{system_message}\n\n{user_message}"

        # Get Use Cases content from Gemini
        use_cases_content = None
        for attempt in range(self.max_retries):
            use_cases_content = self.call_gemini(full_prompt, temperature=0.3, max_tokens=2000)
            if use_cases_content:
                break
            self.logger.warning(f"Attempt {attempt + 1} failed to generate use cases content")
        
        if not use_cases_content:
            self.logger.error("Failed to generate use cases content after all retries")
            use_cases_content = "Failed to generate use cases content."

        # Return all contents for use in next sections
        return {
            "introduction": previous_contents["introduction"],
            "overall_description": previous_contents["overall_description"],
            "system_features": previous_contents["system_features"],
            "external_interfaces": previous_contents["external_interfaces"],
            "non_functional_requirements": previous_contents["non_functional_requirements"],
            "use_cases": use_cases_content
        }