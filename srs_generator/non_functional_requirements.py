from .rag import AgentBase
from .first_page import SRSConcrete

class NonFunctionalRequirementsAgent(AgentBase):
    def __init__(self, max_retries=2, verbose=True):
        super().__init__(name="NonFunctionalRequirementsAgent", max_retries=max_retries, verbose=verbose)
        self.srs = SRSConcrete("SRSWriter", max_retries, verbose)

    def execute(self, topic, previous_contents):
        messages = [
            {
                "role": "system",
                "content": """You are an expert system requirement specification document writer. Based on all previous sections provided, write a comprehensive non-functional requirements section that includes:

                7.1 Performance Requirements: 
                - Speed, latency, and response time requirements.
                - Maximum concurrent users and system load capacity.
                - Data processing times and throughput.

                7.2 Security Requirements:
                - Data security and encryption standards.
                - Authentication and authorization mechanisms.
                - Protection against data breaches and cyber threats.
                - Compliance with security regulations (e.g., GDPR, CCPA).

                7.3 Reliability Requirements:
                - Uptime and availability targets (e.g., 99.9% uptime).
                - Backup and disaster recovery mechanisms.
                - Error detection and self-healing features.

                7.4 Usability Requirements:
                - User experience standards and accessibility guidelines.
                - Ease of navigation and learnability.
                - Multi-language support (if applicable).

                7.5 Scalability Requirements:
                - Support for increasing user load and data growth.
                - Horizontal and vertical scaling capabilities.
                - Performance under peak load conditions.

                7.6 Maintainability Requirements:
                - Code structure and modularity.
                - Ease of debugging and updating.
                - Automated testing and CI/CD integration.

                7.7 Compliance Requirements:
                - Legal or regulatory compliance (e.g., GDPR, ISO 27001).
                - Data retention policies and audit requirements.
                - Compliance with industry-specific standards.

                7.8 Availability Requirements:
                - System uptime and fault tolerance.
                - Offline mode functionality and data synchronization.
                - Redundancy and failover mechanisms.

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
                    "Please write the Non-functional Requirements section that aligns with all previous sections:"
                )
            }
        ]

        # Get Non-functional Requirements content from Llama
        non_func_content = self.call_llama(messages, temperature=0.3, max_tokens=2000)
        

        
        # Return all contents for use in next sections
        return {
            "introduction": previous_contents["introduction"],
            "overall_description": previous_contents["overall_description"],
            "system_features": previous_contents["system_features"],
            "external_interfaces": previous_contents["external_interfaces"],
            "non_functional_requirements": non_func_content
        }
