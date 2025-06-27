import time
from loguru import logger
from .first_page import SRSConcrete
from .introduction import IntroductionAgent
from .overall_description import OverallDescriptionAgent
from .system_feature import SystemFeaturesAgent
from .external_interface_requirements import ExternalInterfaceAgent
from .non_functional_requirements import NonFunctionalRequirementsAgent
from .use_cases import UseCasesAgent
from .system_models_diagrams import SystemModelsAgent

class SRSAgentManager:
    def __init__(self, name="SRSAgentManager", max_retries=5, verbose=True):
        self.name = name
        self.max_retries = max_retries
        self.verbose = verbose
        self.srs_writer = SRSConcrete("SRSWriter", max_retries, verbose)
        self.introduction_agent = IntroductionAgent(max_retries, verbose)
        self.overall_description_agent = OverallDescriptionAgent(max_retries, verbose)
        self.system_features_agent = SystemFeaturesAgent(max_retries, verbose)
        self.external_interface_agent = ExternalInterfaceAgent(max_retries, verbose)
        self.non_functional_requirements_agent = NonFunctionalRequirementsAgent(max_retries, verbose)
        self.use_cases_agent = UseCasesAgent(max_retries, verbose)
        self.system_models_agent = SystemModelsAgent(max_retries, verbose)
        self.logger = logger

    def generate_srs(self, topic, user_name, file_name="SRS_document.docx"):
        """
        Orchestrates the generation of SRS document
        """
        try:
            self.logger.info(f"[{self.name}] Starting SRS generation")

            # Create first page
            self.logger.info(f"[{self.name}] Creating first page")
            self.srs_writer.create_first_page(user_name=user_name, file_name=file_name)

            # Generate content for each section
            contents = {}
            
            # Generate Introduction
            self.logger.info(f"[{self.name}] Generating Introduction")
            contents = self.introduction_agent.execute(topic, contents)
            time.sleep(2)  # Reduced delay for better performance

            # Generate Overall Description
            self.logger.info(f"[{self.name}] Generating Overall Description")
            contents = self.overall_description_agent.execute(topic, contents)
            time.sleep(2)

            # Generate System Features
            self.logger.info(f"[{self.name}] Generating System Features")
            contents = self.system_features_agent.execute(topic, contents)
            time.sleep(2)

            # Generate External Interface Requirements
            self.logger.info(f"[{self.name}] Generating External Interface Requirements")
            contents = self.external_interface_agent.execute(topic, contents)
            time.sleep(2)

            # Generate Non-functional Requirements
            self.logger.info(f"[{self.name}] Generating Non-functional Requirements")
            contents = self.non_functional_requirements_agent.execute(topic, contents)
            time.sleep(2)

            # Generate Use Cases
            self.logger.info(f"[{self.name}] Generating Use Cases")
            contents = self.use_cases_agent.execute(topic, contents)
            time.sleep(2)

            # Write all contents to document
            self.logger.info(f"[{self.name}] Writing contents to document")
            self.srs_writer.add_page(contents, file_name)

            # Generate System Models and Diagrams
            self.logger.info(f"[{self.name}] Generating System Models and Diagrams")
            contents = self.system_models_agent.execute(topic, contents, file_name)

            self.logger.info(f"[{self.name}] SRS document generation completed successfully")
            return file_name
        except Exception as e:
            self.logger.error(f"[{self.name}] Failed to generate SRS document: {str(e)}")
            raise