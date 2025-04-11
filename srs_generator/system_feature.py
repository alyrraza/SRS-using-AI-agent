#system feature.py
from .rag import AgentBase
from .first_page import SRSConcrete

class SystemFeaturesAgent(AgentBase):
   def __init__(self, max_retries=2, verbose=True):
       super().__init__(name="SystemFeaturesAgent", max_retries=max_retries, verbose=verbose)
       self.srs = SRSConcrete("SRSWriter", max_retries, verbose)

   def execute(self, topic, previous_contents):
       messages = [
           {
               "role": "system",
               "content": """You are an expert system requirement specification document writer. Based on the introduction and overall description provided, write a detailed system features section.

               For each major feature mentioned in the previous sections, provide:

               5.x Feature Name: (Meaningful name of the feature)
               Description: Detailed overview of what the feature does
               Input: Required data inputs for this feature
               Output: Expected outputs or results
               Priority: Importance level (High, Medium, Low)
               Functional Requirements: Detailed requirements numbered as FR 5.x.1, FR 5.x.2, etc.

               Format each feature consistently using the structure above.
               Ensure features align with the product functions mentioned in the overall description.
               Number features as 5.1, 5.2, etc.
               """
           },
           {
               "role": "user",
               "content": (
                   f"Here is the project description:\n{topic}\n\n"
                   f"Here is the introduction:\n{previous_contents['introduction']}\n\n"
                   f"Here is the overall description:\n{previous_contents['overall_description']}\n\n"
                   "Please write the System Features section that aligns with these previous sections:"
               )
           }
       ]
       
       # Get system features content from Llama
       features_content = self.call_llama(messages, temperature=0.3, max_tokens=2000)
       
       
       # Return all contents for use in next sections
       return {
           "introduction": previous_contents["introduction"],
           "overall_description": previous_contents["overall_description"],
           "system_features": features_content
       }