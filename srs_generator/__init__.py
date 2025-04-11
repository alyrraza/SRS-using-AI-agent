from .first_page import SRSConcrete
from .introduction import IntroductionAgent
from .overall_description import OverallDescriptionAgent
from .system_feature import SystemFeaturesAgent
from .external_interface_requirements import ExternalInterfaceAgent
from .non_functional_requirements import NonFunctionalRequirementsAgent
from .use_cases import UseCasesAgent
from .system_models_diagrams import SystemModelsAgent
from loguru import logger

class SRSAgentManager:
    def __init__(self, max_retries=2, verbose=True):
        self.agents = {
            "introduction": IntroductionAgent(max_retries=max_retries, verbose=verbose),
            "overall_description": OverallDescriptionAgent(max_retries=max_retries, verbose=verbose),
            "system_features": SystemFeaturesAgent(max_retries=max_retries, verbose=verbose),
            "external_interfaces": ExternalInterfaceAgent(max_retries=max_retries, verbose=verbose),
            "non_functional_requirements": NonFunctionalRequirementsAgent(max_retries=max_retries, verbose=verbose),
            "use_cases": UseCasesAgent(max_retries=max_retries, verbose=verbose),
            "system_models": SystemModelsAgent(max_retries=max_retries, verbose=verbose)
        }
        self.srs_concrete = SRSConcrete("SRSWriter", max_retries, verbose)

    def generate_srs(self, user_input, user_name, file_name):
        try:
            logger.info("[SRSAgentManager] Starting SRS generation")

            # Step 1: Create the First Page
            logger.info("[SRSAgentManager] Creating first page")
            self.srs_concrete.create_first_page(user_name, file_name)

            # Step 2: Generate Introduction
            logger.info("[SRSAgentManager] Generating Introduction")
            intro_content = self.agents["introduction"].execute(user_input)

            # Step 3: Generate Overall Description
            logger.info("[SRSAgentManager] Generating Overall Description")
            overall_desc_content = self.agents["overall_description"].execute(user_input, intro_content)

            # Step 4: Generate System Features
            logger.info("[SRSAgentManager] Generating System Features")
            system_features_content = self.agents["system_features"].execute(user_input, overall_desc_content)

            # Step 5: Generate External Interface Requirements
            logger.info("[SRSAgentManager] Generating External Interface Requirements")
            external_interfaces_content = self.agents["external_interfaces"].execute(user_input, system_features_content)

            # Step 6: Generate Non-functional Requirements
            logger.info("[SRSAgentManager] Generating Non-functional Requirements")
            non_func_content = self.agents["non_functional_requirements"].execute(user_input, external_interfaces_content)

            # Step 7: Generate Use Cases
            logger.info("[SRSAgentManager] Generating Use Cases")
            use_cases_content = self.agents["use_cases"].execute(user_input, non_func_content)
            
            self.srs_concrete.add_page(use_cases_content, file_name)

            # Step 8: Generate System Models and Diagrams
            logger.info("[SRSAgentManager] Generating System Models and Diagrams")
            system_models_content = self.agents["system_models"].execute(user_input, use_cases_content, file_name)


            logger.info("[SRSAgentManager] SRS document generation completed successfully")
            
            # Return the complete SRS content
            return system_models_content
        
        except Exception as e:
            logger.error(f"[SRSAgentManager] Error during SRS generation: {e}")
            raise
