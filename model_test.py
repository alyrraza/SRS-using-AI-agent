import subprocess
import os
import requests
import re
from docx import Document
from docx.shared import Inches
from loguru import logger
from dotenv import load_dotenv

class SystemModelsAgent:
    def __init__(self, max_retries=2, verbose=True):
        self.name = "SystemModelsAgent"
        self.max_retries = max_retries
        self.verbose = verbose
        load_dotenv()
        self.diagram_types = {
            "ActivityDiagram": """Generate a detailed PlantUML Activity Diagram for the use cases.
                                Rules:
                                1. Include start and stop nodes
                                2. Show all decision points with if/else conditions
                                3. Include major user actions and system responses
                                4. Use correct PlantUML syntax for activity diagrams
                                5. Only generate PlantUML code, no explanations
                                
                                Example of correct syntax:
                                @startuml
                                start
                                :User opens application;
                                if (Is user logged in?) then (yes)
                                    :Show dashboard;
                                else (no)
                                    :Show login form;
                                    :User enters credentials;
                                    if (Credentials valid?) then (yes)
                                        :Show dashboard;
                                    else (no)
                                        :Show error message;
                                    endif
                                endif
                                :User performs action;
                                stop
                                @enduml""",
            
            "SequenceDiagram": """Generate a detailed PlantUML Sequence Diagram for interactions between actors and system components.
                                Rules:
                                1. Include relevant actors and system components
                                2. Show the complete sequence of interactions
                                3. Use proper arrow types (-> for requests, --> for responses)
                                4. Include important system operations
                                5. Only generate PlantUML code, no explanations
                                
                                Example of correct syntax:
                                @startuml
                                actor User
                                participant Frontend
                                participant Backend
                                database Database
                                
                                User -> Frontend: Access application
                                Frontend -> Backend: Request authentication
                                Backend -> Database: Validate credentials
                                Database --> Backend: Return user data
                                Backend --> Frontend: Authentication result
                                Frontend --> User: Show dashboard
                                @enduml"""
        }
        self.diagrams = {}
    
    def generate_diagram_code(self, diagram_type, use_cases):
        """Generate PlantUML code using Gemini API"""
        prompt = self.diagram_types[diagram_type]
        full_prompt = (
            f"{prompt}\n"
            f"Use Cases:\n{use_cases}\n\n"
            "Important: Only generate PlantUML code. "
            "Start with @startuml and end with @enduml. "
            "Do not include any explanations or extra text."
        )

        # Call Gemini API
        for attempt in range(3):
            response = self.call_gemini(full_prompt)
            plantuml_code = self.extract_plantuml(response)
            
            if plantuml_code:
                return plantuml_code
                    
            logger.warning(f"Attempt {attempt + 1}: Invalid PlantUML code generated")
        
        logger.error("Failed to generate valid PlantUML code after 3 attempts")
        return None


    def call_gemini(self, prompt):
        """Call Gemini API to generate PlantUML code"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            json_response = response.json()
            try:
                text = json_response['candidates'][0]['content']['parts'][0]['text']
                return text
            except (IndexError, KeyError, TypeError) as e:
                logger.error(f"Error parsing Gemini response: {e}")
                return None
        else:
            logger.error(f"Gemini API call failed: {response.text}")
            return None

    def extract_plantuml(self, text):
        """Extract PlantUML code between @startuml and @enduml tags"""
        match = re.search(r'(@startuml[\s\S]*?@enduml)', text, re.DOTALL)
        if not match:
            logger.error("No valid PlantUML code found in the response")
            return None
        
        # Clean up the extracted code
        code = match.group(1)
        code = re.sub(r'\s+', ' ', code)  # Normalize whitespace
        code = code.replace(' @', '@')    # Fix tag spacing
        return code

    def create_diagram(self, name, plantuml_code, jar_path = os.path.abspath("./lib/plantuml.jar")):
        """Generate PNG from PlantUML code using PlantUML JAR"""
        if not plantuml_code:
            return None
            
        if not os.path.exists(jar_path):
            logger.error(f"PlantUML jar not found at: {jar_path}")
            return None
            
        try:
            # Create diagrams directory if it doesn't exist
            os.makedirs("diagrams", exist_ok=True)
            
            # Save PUML file
            puml_file = os.path.join("diagrams", f"{name}.puml")
            with open(puml_file, "w", encoding='utf-8') as f:
                f.write(plantuml_code)
            
            # Generate PNG
            result = subprocess.run(
            ["java", "-jar", f'"{jar_path}"', puml_file],
            check=True,
            capture_output=True,
            text=True,
            shell=True  # Add shell=True to handle spaces in path
)

            
            png_path = os.path.join("diagrams", f"{name}.png")
            if os.path.exists(png_path):
                logger.info(f"{name}.png generated successfully")
                return png_path
            else:
                logger.error(f"PNG file not generated for {name}")
                logger.error(f"PlantUML output: {result.stdout}\n{result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating diagram {name}: {str(e)}")
            return None

    def execute(self, use_cases):
        """Main execution method to generate diagrams based on use cases"""
        # Generate diagrams
        for diagram_type in self.diagram_types:
            plantuml_code = self.generate_diagram_code(diagram_type, use_cases)
            if plantuml_code:
                self.diagrams[diagram_type] = plantuml_code
                logger.info(f"{diagram_type} generated successfully")
                # Create diagram as PNG
                self.create_diagram(diagram_type, plantuml_code)

        return self.diagrams

# Example Usage
if __name__ == "__main__":
    use_cases = """
    1. User Registration:
       - User enters personal details and creates an account
       - System validates the information and stores it in the database
    2. Product Purchase:
       - User selects products and adds them to the cart
       - User proceeds to checkout and makes a payment
       - System verifies payment and confirms the order
    """
    
    agent = SystemModelsAgent()
    diagrams = agent.execute(use_cases)
    
    # Output generated PlantUML code for testing
    for diagram_type, code in diagrams.items():
        print(f"\n{diagram_type}:\n{code}")
