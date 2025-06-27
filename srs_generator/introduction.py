import os
from .rag import AgentBase
from .first_page import SRSConcrete
from loguru import logger
from dotenv import load_dotenv

class IntroductionAgent(AgentBase):
    def __init__(self, max_retries=5, verbose=True):
        super().__init__(name="IntroductionAgent", max_retries=max_retries, verbose=verbose)
        self.srs = SRSConcrete("SRSWriter", max_retries, verbose)
        load_dotenv()
        self.logger = logger

    def execute(self, topic, previous_contents):
        # Construct the prompt by combining system and user messages
        system_message = """You are an expert system requirement specification document writer. Based on the project description provided, write a comprehensive Introduction section for the Cold Calling Agent system, including in this format:

        **1.1** Purpose: State the purpose of the SRS document, including the intended audience (e.g., developers, stakeholders).
        **1.2** Scope: Describe the system's features (e.g., lead ingestion, AI content generation, email and call automation), objectives, and benefits.
        **1.3** Definitions, Acronyms, and Abbreviations: Define key terms (e.g., **CRM**, **LLM**, **API**, **temp.com**, **Vapi.ai**, **n8n**) using Markdown bold syntax (**term**) for each term.
        **1.4** References: List any referenced documents or resources (e.g., n8n.io documentation, Vapi.ai API specs).
        **1.5** Overview: Provide a brief overview of the SRS document structure.

        Format Rules:
        1. Start directly with subsection 1.1 Purpose (do NOT include the top-level heading '1. Introduction').
        2. Return ONLY the section content without any conversational preamble (e.g., do NOT include 'Here is the Introduction section').
        3. Use Markdown bold syntax (**term**) for defined terms in 1.3 Definitions, Acronyms, and Abbreviations.
        4. Use clear, professional language suitable for an SRS document.
        5. Don't write the main heading e.g. 1. Introduction, as it has already been added.
        """

        user_message = (
            f"Project description:\n{topic}\n\n"
            f"Generate the Introduction section for the Cold Calling Agent system, starting with subsection 1.1 Purpose."
        )

        # Combine system and user messages
        messages = [
            self.format_message("system", system_message),
            self.format_message("user", user_message)
        ]

        # Get introduction content from Gemini
        intro_content = None
        for attempt in range(self.max_retries):
            response = self.call_gemini(messages, temperature=0.3, max_tokens=1024)

            # Extract actual content safely
            if isinstance(response, dict) and "text" in response:
                intro_content = response["text"]
            elif isinstance(response, str):
                intro_content = response
            else:
                self.logger.error(f"[{self.name}] Unexpected Gemini response format: {type(response).__name__}")
                intro_content = None

            if intro_content:
                break
            self.logger.warning(f"[{self.name}] Attempt {attempt + 1} failed to generate introduction content")
        
        if not intro_content:
            self.logger.error(f"[{self.name}] Failed to generate introduction content after all retries")
            intro_content = "Failed to generate introduction content."

        # Update previous_contents with string content
        previous_contents["introduction"] = intro_content
        return previous_contents
    