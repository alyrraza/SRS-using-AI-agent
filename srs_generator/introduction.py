#introduction.py
from .rag import AgentBase
from .first_page import SRSConcrete

class IntroductionAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="IntroductionAgent", max_retries=max_retries, verbose=verbose)
        self.srs = SRSConcrete("SRSWriter", max_retries, verbose)

    def execute(self, topic):
        # First generate the introduction using LLama
        messages = [
            {
                "role": "system",
                "content": """You are an expert system requirement specification document writer who will write a good introduction of a provided description 
                which includes 
                Purpose: State the purpose of the SRS document, including the intended audience.
                3.2 Scope: Describe the system's features, objectives, and benefits.
                3.3 Definitions, Acronyms, and Abbreviations: Define key terms, acronyms, and abbreviations used.
                3.4 Document Conventions: Specify formatting rules and numbering schemes.
                3.5 Intended Audience and Reading Suggestions: Specify who should read the document and in what order.
                """
            },
            {
                "role": "user",
                "content": (
                    "please write the introduction for SRS docs of the following description : \n\n"
                    f"{topic}\n\n here is the description:"
                )
            }
        ]
        
        # Get introduction content from LLama
        intro_content = self.call_llama(messages, temperature=0.3, max_tokens=1024)
        
        
        return intro_content