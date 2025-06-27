import os
import requests
from .rag import AgentBase
from .first_page import SRSConcrete
from loguru import logger
from dotenv import load_dotenv

class ExternalInterfaceAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="ExternalInterfaceAgent", max_retries=max_retries, verbose=verbose)
        self.srs = SRSConcrete("SRSWriter", max_retries, verbose)
        load_dotenv()
        self.logger = logger
    '''
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
    '''
    def execute(self, topic, previous_contents):
        # Construct the prompt by combining system and user messages
        system_message = """You are an expert system requirement specification document writer. Based on all previous sections provided, write a comprehensive external interface requirements section that includes:

        **4.1 User Interfaces**: 
        **4.1.1** Detailed description of UI design and functionality
        **4.1.2** Screen layouts and user interaction flows
        **4.1.3** Response time requirements
        **4.1.4** UI standards and guidelines

        **4.2 Hardware Interfaces**:
        **4.2.1** Required hardware components and devices
        **4.2.2** Interface characteristics and protocols
        **4.2.3** Communication methods with hardware
        **4.2.4** Physical connectivity requirements

        **4.3 Software Interfaces**:
        **4.3.1** External software systems and APIs
        **4.3.2** Data formats and exchange protocols
        **4.3.3** Third-party service integrations
        **4.3.4** Communication methods and frequencies

        **4.4 Communication Interfaces**:
        **4.4.1** Network protocols and standards
        **4.4.2** Communication security requirements
        **4.4.3** Data format specifications
        **4.4.4** Bandwidth and timing requirements
        Format Rules:
        1. Use clear, structured headings for each subsection and add double asterisks (e.g., **4.1 User Interfaces**, **4.2 Hardware Interfaces**).
        2. Return ONLY the section content without any conversational preamble (e.g., do NOT include 'Here is the Overall Description section' or similar text).
        3. Ensure content aligns with the provided introduction and project description.
        4. Use clear, professional language suitable for an SRS document.
        5. Don't write the main heading e.g. 4. External Interface Requirements, as it has already been added.
        Ensure alignment with previously defined features and requirements.
        """
        
        user_message = (
            f"Here is the project description:\n{topic}\n\n"
            f"Here is the introduction:\n{previous_contents['introduction']}\n\n"
            f"Here is the overall description:\n{previous_contents['overall_description']}\n\n"
            f"Here are the system features:\n{previous_contents['system_features']}\n\n"
            "Please write the External Interface Requirements section that aligns with all previous sections:"
            "Ive already added the main heading e.g. 4. External Interface Requirements, so you can start with the first subsection 4.1 User Interfaces."
        )

        # Combine system and user messages
        messages = [
            self.format_message("system", system_message),
            self.format_message("user", user_message)
        ]

        # Get external interface requirements content from Gemini
        interface_content = None
        for attempt in range(self.max_retries):
            interface_content = self.call_gemini(messages, temperature=0.3, max_tokens=1024)
            if interface_content:
                break
            self.logger.warning(f"[{self.name}] Attempt {attempt + 1} failed to generate external interface requirements content")
        
        if not interface_content:
            self.logger.error(f"[{self.name}] Failed to generate external interface requirements content after all retries")
            interface_content = "Failed to generate external interface requirements content."

        # Return all contents for use in next sections
        return {
            "introduction": previous_contents["introduction"],
            "overall_description": previous_contents["overall_description"],
            "system_features": previous_contents["system_features"],
            "external_interfaces": interface_content
        }