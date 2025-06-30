# SRS Generator

**SRS Generator** is an AI-powered web application that automates the creation of Software Requirements Specification (**SRS**) documents in `.docx` format.

Built with **Streamlit**, **Python**, and the **Gemini API**, it follows a modular, n8n-inspired pipeline architecture to generate professional documents including sections like *Introduction*, *System Features*, and *UML Diagrams*.

---

##  Introduction

The **SRS Generator** simplifies SRS creation by taking user inputs (name, project description, file name) and producing a structured `.docx` file.

Its **modular design**, inspired by automation tools like *n8n* and *make.com*, makes it extensible and ideal for experimentation.

It leverages:

- **Gemini API** for AI-generated content  
- **python-docx** for document formatting  
- **PlantUML** for UML diagrams  

---

##  Features

-  **AI Automation**: Generates SRS content using the **Gemini API**
-  **Modular Architecture**: Dedicated agents handle each section (e.g., `IntroductionAgent`, `SystemFeaturesAgent`)
-  **n8n-Inspired Pipeline**: Sequential agent-based workflow
-  **Professional Formatting**: Headings, bullet points, and bold Markdown-style text (e.g., `**CRM**`, `**API**`)
-  **UML Diagrams**: Automatically inserts Use Case, Sequence, and Class diagrams via **PlantUML**
-  **Robust Logging & Retries**: Includes `max_retries=5` and `loguru` logging
-  **Great for Learning**: Offers experience in AI integration, pipeline architecture, and modular development

---

##  Workflow

1. **User Input**: Enter your **name**, **project description**, and **file name** in the Streamlit interface.
2. **Pipeline Execution**:
   - `SRSAgentManager` coordinates agent execution
   - `SRSConcrete.create_first_page()` creates the title page
   - Agents (e.g., `IntroductionAgent`) generate content using Gemini API
   - `SRSConcrete.add_page()` formats content into a DOCX
   - `SystemModelsAgent` embeds UML diagrams
3. **Output**: Download the `.docx` file and **update the TOC manually** in MS Word (`Ctrl+A`, then `F9`)

---

##  Installation

```bash
# Clone the repository
gh repo clone alyrraza/SRS-using-AI-agent

# Install dependencies
pip install -r requirements.txt
```

###  Set up `.env`

```env
GEMINI_API_KEY=your_api_key
PLANTUML_JAR_PATH=/path/to/plantuml.jar
```

📥 Download `plantuml-mit-1.2025.0.jar` and place it in a `lib/` folder, or update `PLANTUML_JAR_PATH`.

---

##  Usage

```bash
streamlit run main.py
```

In the Streamlit interface:

1. Enter your name (e.g., `John Doe`)
2. Paste the project description (e.g., AI-based cold calling system)
3. Specify a file name (e.g., `AIAGENT`)
4. Click **"Generate SRS"**
5. Download the `.docx` file
6. Open in Microsoft Word and press `Ctrl+A`, then `F9` to update the TOC

---

##  Example

**Input**:

- User Name: `John Doe`
- Project Description: *A system for automating lead outreach with AI-generated emails and calls, integrated with n8n and Vapi.ai.*
- File Name: `AIAGENT`

**Output**: `AIAGENT.docx` with:

-  Title Page
-  Structured Sections (Introduction, Overall Description, etc.)
-  Embedded UML Diagrams
-  Placeholder TOC (manually update with `Ctrl+A`, `F9`)

---

##  Limitations

-  **Table of Contents**: Needs manual refresh in Word (`Ctrl+A`, `F9`)
-  **API Dependency**: Requires a valid **Gemini API Key**

---

##  Project Structure

```
  srs-generator/
├── main.py                  # Streamlit entry point
├── __init__.py              # Pipeline manager
├── first_page.py            # Title and content formatting
├── introduction.py          # Introduction agent
├── overall_description.py   # Other content agents
├── system_models_diagrams.py # UML diagram generator
├── rag.py                   # Gemini API interaction
├── .env                     # Environment config
```

---

## Experimentation Ideas

-  **n8n Integration**: Use SRS generation as part of real-time workflows
-  **Custom Agents**: Add agents for new sections like glossary, data models
-  **Local AI Models**: Swap Gemini for local models (e.g., Phi-3 Mini)
-  **Enhanced Diagrams**: Extend PlantUML with custom styling

---

## How to Use

To get started:

- Clone the repository
- Install the required dependencies
- Run the Streamlit app

```bash
# Step 1: Clone the repo
git clone https://github.com/alyrraza/SRS-using-AI-agent
cd SRS-using-AI-agent

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Run the app
streamlit run main.py
```

##  Benefits for Software Teams

-  Saves time in SRS documentation
-  Encourages AI-based development workflows
-  Promotes modular and scalable design practices
-  Ideal for experimentation and educational use

---

##  Contributing

Pull requests and issues are welcome!

Feel free to:

- Submit new agents  
- Improve diagram handling  
- Refactor or optimize pipelines  

---


