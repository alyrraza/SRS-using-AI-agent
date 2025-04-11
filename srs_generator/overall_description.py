#overall description.py
from .rag import AgentBase
from .first_page import SRSConcrete

class OverallDescriptionAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="OverallDescriptionAgent", max_retries=max_retries, verbose=verbose)
        self.srs = SRSConcrete("SRSWriter", max_retries, verbose)

    def execute(self, topic, intro_content):
        messages = [
            {
                "role": "system",
                "content": """You are an expert system requirement specification document writer. Based on the introduction provided, write a comprehensive overall description section that includes:

                4.1 Product Perspective: Describe the product's context, including system interfaces and dependencies.
                4.2 Product Functions: High-level overview of the system's major functionalities.
                4.3 User Classes and Characteristics: Identify the types of users (e.g., Admin, Regular User).
                4.4 Operating Environment: Specify hardware, software, and network requirements.
                4.5 Design and Implementation Constraints: Highlight limitations like technology choices or legal constraints.
                4.6 Assumptions and Dependencies: Assumptions that may impact requirements.

                Keep your response consistent with the introduction provided.
                """
            },
            {
                "role": "user",
                "content": (
                    f"Here is the project description:\n{topic}\n\n"
                    f"And here is the introduction already written:\n{intro_content}\n\n"
                    "Please write the Overall Description section that aligns with this introduction:"
                )
            }
        ]
        
        # Get overall description content from Llama
        overall_desc_content = self.call_llama(messages, temperature=0.3, max_tokens=1500)
        
        # Return both contents for use in next sections
        return {
            "introduction": intro_content,
            "overall_description": overall_desc_content
        }