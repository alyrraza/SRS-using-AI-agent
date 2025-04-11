import streamlit as st
import os
from srs_generator import SRSAgentManager

def main():
    # Set page config
    st.set_page_config(
        page_title="SRS Generator",
        page_icon="📝",
        layout="wide"
    )

    # Add title and description
    st.title("Software Requirements Specification (SRS) Generator")
    st.markdown("""
    Generate a professional SRS document by providing your project description.
    The system will analyze your input and create a comprehensive SRS document.
    """)

    # Create form
    with st.form("srs_form"):
        # Add username input
        user_name = st.text_input(
            "Enter your name:",
            placeholder="e.g., John Doe",
            help="Your name will be used in the generated document"
        )

        # Add filename input with .docx extension handling
        file_name = st.text_input(
            "Enter file name:",
            placeholder="e.g., Project_SRS",
            help="The document will be saved as a .docx file"
        )

        # Add large text area for project description
        user_input = st.text_area(
            "Enter your project description:",
            height=300,
            placeholder="Describe your project here... (e.g., features, functionalities, user interactions)",
            help="Provide a detailed description of your project. The more detailed your description, the better the generated SRS will be."
        )

        # Add submit button
        submit_button = st.form_submit_button("Generate SRS")

    # Handle form submission
    if submit_button:
        if not user_name or not file_name or not user_input:
            st.error("Please fill in all fields")
            return

        # Add .docx extension if not present
        if not file_name.endswith('.docx'):
            file_name += '.docx'

        # Show processing message
        with st.spinner("Generating SRS Document... This may take a few minutes."):
            try:
                # Initialize SRS manager and generate document
                srs_manager = SRSAgentManager()
                srs_content = srs_manager.generate_srs(user_input, user_name, file_name)

                # Check if file was created
                if os.path.exists(file_name):
                    # Success message with download button
                    st.success("SRS Document generated successfully!")
                    
                    # Read the generated file
                    with open(file_name, "rb") as file:
                        btn = st.download_button(
                            label="Download SRS Document",
                            data=file,
                            file_name=file_name,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error("Error: File was not generated properly")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Add usage instructions in an expander
    with st.expander("How to use"):
        st.markdown("""
        1. **Enter your name**: This will be used in the document metadata
        2. **Enter file name**: Choose a name for your SRS document (`.docx` will be added automatically)
        3. **Enter project description**: Provide a detailed description of your project including:
            - Main features and functionalities
            - User interactions
            - System requirements
            - Any specific constraints or requirements
        4. **Click Generate SRS**: The system will process your input and create a comprehensive SRS document
        5. **Download**: Once generated, you can download the document using the download button
        """)

    # Add footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <p>SRS Generator Tool • Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()