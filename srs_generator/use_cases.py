from .rag import AgentBase
from .first_page import SRSConcrete

class UseCasesAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="UseCasesAgent", max_retries=max_retries, verbose=verbose)
        self.srs = SRSConcrete("SRSWriter", max_retries, verbose)

    def execute(self, topic, previous_contents):
        messages = [
            {
                "role": "system",
                "content": """You are an expert system requirement specification document writer. Based on all previous sections provided, write a comprehensive Use Cases section that includes:

                10. Use Cases:
                - Detailed scenarios for each primary feature or interaction.
                - Include the following for each use case:

                10.1 Use Case Name (e.g., Real-Time Monitoring)
                - Actors: Users or systems interacting with the feature.
                - Description: Detailed scenario of the use case.
                - Preconditions: Conditions that must be met before the use case.
                - Postconditions: Expected state after the use case is executed.
                - Main Flow: Primary sequence of steps.
                - Alternate Flows: Variations or exceptions in the flow.
                
                Ensure alignment with previously defined features and requirements.
                """
            },
            {
                "role": "user",
                "content": (
                    f"Here is the project description:\n{topic}\n\n"
                    f"Here is the introduction:\n{previous_contents['introduction']}\n\n"
                    f"Here is the overall description:\n{previous_contents['overall_description']}\n\n"
                    f"Here are the system features:\n{previous_contents['system_features']}\n\n"
                    f"Here are the external interfaces:\n{previous_contents['external_interfaces']}\n\n"
                    f"Here are the non-functional requirements:\n{previous_contents['non_functional_requirements']}\n\n"
                    "Please write the Use Cases section that aligns with all previous sections:"
                )
            }
        ]

        # Get Use Cases content from Llama
        use_cases_content = self.call_llama(messages, temperature=0.3, max_tokens=2000)

        
        # Return all contents for use in next sections
        return {
            "introduction": previous_contents["introduction"],
            "overall_description": previous_contents["overall_description"],
            "system_features": previous_contents["system_features"],
            "external_interfaces": previous_contents["external_interfaces"],
            "non_functional_requirements": previous_contents["non_functional_requirements"],
            "use_cases": use_cases_content
        }
