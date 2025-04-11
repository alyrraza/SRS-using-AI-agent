from .rag import AgentBase
from .first_page import SRSConcrete

class ExternalInterfaceAgent(AgentBase):
   def __init__(self, max_retries=2, verbose=True):
       super().__init__(name="ExternalInterfaceAgent", max_retries=max_retries, verbose=verbose)
       self.srs = SRSConcrete("SRSWriter", max_retries, verbose)

   def execute(self, topic, previous_contents):
       messages = [
           {
               "role": "system",
               "content": """You are an expert system requirement specification document writer. Based on all previous sections provided, write a comprehensive external interface requirements section that includes:

               6.1 User Interfaces: 
               - Detailed description of UI design and functionality
               - Screen layouts and user interaction flows
               - Response time requirements
               - UI standards and guidelines

               6.2 Hardware Interfaces:
               - Required hardware components and devices
               - Interface characteristics and protocols
               - Communication methods with hardware
               - Physical connectivity requirements

               6.3 Software Interfaces:
               - External software systems and APIs
               - Data formats and exchange protocols
               - Third-party service integrations
               - Communication methods and frequencies

               6.4 Communication Interfaces:
               - Network protocols and standards
               - Communication security requirements
               - Data format specifications
               - Bandwidth and timing requirements

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
                   "Please write the External Interface Requirements section that aligns with all previous sections:"
               )
           }
       ]
       
       # Get external interface requirements content from Llama
       interface_content = self.call_llama(messages, temperature=0.3, max_tokens=2000)


       
       # Return all contents for use in next sections
       return {
           "introduction": previous_contents["introduction"],
           "overall_description": previous_contents["overall_description"],
           "system_features": previous_contents["system_features"],
           "external_interfaces": interface_content
       }