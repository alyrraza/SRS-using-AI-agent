import os
import requests
from .rag import AgentBase
from .first_page import SRSConcrete
from loguru import logger
from dotenv import load_dotenv

class NonFunctionalRequirementsAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="NonFunctionalRequirementsAgent", max_retries=max_retries, verbose=verbose)
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
            self.logger.error(f"[{self.name}] Gemini API call failed: {str(e)}")
            return None

    def execute(self, topic, previous_contents):
        # Construct the prompt by combining system and user messages
        system_message = """You are an expert system requirement specification document writer. Based on all previous sections provided, write a comprehensive non-functional requirements section that includes:

        5.1 Performance Requirements: 
        - Speed, latency, and response time requirements.
        - Maximum concurrent users and system load capacity.
        - Data processing times and throughput.

        5.2 Security Requirements:
        - Data security and encryption standards.
        - Authentication and authorization mechanisms.
        - Protection against data breaches and cyber threats.
        - Compliance with security regulations (e.g., GDPR, CCPA).

        5.3 Reliability Requirements:
        - Uptime and availability targets (e.g., 99.9% uptime).
        - Backup and disaster recovery mechanisms.
        - Error detection and self-healing features.

        5.4 Usability Requirements:
        - User experience standards and accessibility guidelines.
        - Ease of navigation and learnability.
        - Multi-language support (if applicable).

        5.5 Scalability Requirements:
        - Support for increasing user load and data growth.
        - Horizontal and vertical scaling capabilities.
        - Performance under peak load conditions.

        5.6 Maintainability Requirements:
        - Code structure and modularity.
        - Ease of debugging and updating.
        - Automated testing and CI/CD integration.

        5.7 Compliance Requirements:
        - Legal or regulatory compliance (e.g., GDPR, ISO 27001).
        - Data retention policies and audit requirements.
        - Compliance with industry-specific standards.

        5.8 Availability Requirements:
        - System uptime and fault tolerance.
        - Offline mode functionality and data synchronization.
        - Redundancy and failover mechanisms.

        Ensure alignment with previously defined features and requirements.
        """
        
        user_message = (
            f"Here is the project description:\n{topic}\n\n"
            f"Here is the introduction:\n{previous_contents['introduction']}\n\n"
            f"Here is the overall description:\n{previous_contents['overall_description']}\n\n"
            f"Here are the system features:\n{previous_contents['system_features']}\n\n"
            f"Here are the external interfaces:\n{previous_contents['external_interfaces']}\n\n"
            "Please write the Non-functional Requirements section that aligns with all previous sections:"
        )

        # Combine system and user messages into a single prompt
        full_prompt = f"{system_message}\n\n{user_message}"

        # Get Non-functional Requirements content from Gemini
        non_func_content = None
        for attempt in range(self.max_retries):
            non_func_content = self.call_gemini(full_prompt, temperature=0.3, max_tokens=2000)
            if non_func_content:
                break
            self.logger.warning(f"[{self.name}] Attempt {attempt + 1} failed to generate non-functional requirements content")
        
        if not non_func_content:
            self.logger.error(f"[{self.name}] Failed to generate non-functional requirements content after all retries")
            non_func_content = "Failed to generate non-functional requirements content."

        # Return all contents for use in next sections
        return {
            "introduction": previous_contents["introduction"],
            "overall_description": previous_contents["overall_description"],
            "system_features": previous_contents["system_features"],
            "external_interfaces": previous_contents["external_interfaces"],
            "non_functional_requirements": non_func_content
        }