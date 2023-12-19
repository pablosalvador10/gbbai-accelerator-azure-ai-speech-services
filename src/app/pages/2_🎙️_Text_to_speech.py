import streamlit as st
import base64
import os
from datetime import datetime
import uuid

from src.speech_sdk.text_to_speech import synthesize_speech
from utils.ml_logging import get_logger

# Set up logger and environment variables
logger = get_logger()
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")

from src.speech_sdk.speech_to_text import transcribe_speech_from_file_continuous

# Initialize session state variables if they don't exist
if 'transcribed_texts' not in st.session_state:
    st.session_state['transcribed_texts'] = {}

# Function to convert image to base64
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Web user interface
st.markdown(
    f"""
    <h1 style="text-align:center;">
        🎙️ Speach to Text hub ! 
        <br>
        <span style="font-style:italic; font-size:0.7em;">with Azure AI services</span> <img src="data:image/png;base64,{get_image_base64('./utils/images/azure_logo.png')}" alt="logo" style="width:30px;height:30px;">
    </h1>
    """,
    unsafe_allow_html=True,
)

with st.expander("About this App"):
    st.markdown(
        """
    ### 🌟 Application Overview
    This application demonstrates the power of Azure AI in a real-time conversational context. It seamlessly integrates various Azure AI services to provide a sophisticated speech-to-text and text-to-speech experience.

    #### Key Features:
    - **Real-Time Speech Recognition**: Utilizes Azure Speech AI to transcribe speech to text in real-time.
    - **Natural Language Processing**: Employs Azure OpenAI GPT-4 for advanced text comprehension and response generation.
    - **Intent Recognition**: Leverages Azure Language Service to understand and interpret user intentions from speech.

    ### 🔧 Prerequisites and Dependencies
    To fully experience this application, the following Azure services are required:

    - **Azure OpenAI Service**: Set up an instance and obtain an API key for access to GPT-4 capabilities.
    - **Azure Speech AI Service**: Necessary for converting speech to text. A subscription key and region information are needed.
    - **Azure Language Service**: Essential for understanding the context and intent behind spoken language.

    These services combine to create a robust conversational agent capable of understanding and responding to spoken language in a meaningful way.
    """,
        unsafe_allow_html=True,
    )


# Function to download a specific file's transcription
def download_transcription(file_name):
    if file_name in st.session_state['transcribed_texts']:
        return st.session_state['transcribed_texts'][file_name]
    return ""

def clear_conversation_history():
    """
    Clear the conversation history stored in the session state.
    """
    st.session_state["conversation_history"] = []

def save_uploaded_file(uploaded_file):
    # Create a directory for storing uploaded files if it doesn't exist
    upload_directory = os.path.join("src", "app", "uploads")
    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)

    # Generate a session ID and the current date
    st.session_state["conversation_id"] = str(uuid.uuid4())
    st.session_state["conversation_start_time"] = datetime.now()
    date_str = st.session_state["conversation_start_time"].strftime("%Y%m%d")

    # Create a subdirectory with the session ID and date
    subdirectory = os.path.join(upload_directory, f"{st.session_state['conversation_id']}_{date_str}")
    if not os.path.exists(subdirectory):
        os.makedirs(subdirectory)

    # Create a file path
    file_path = os.path.join(subdirectory, uploaded_file.name)

    # Write the uploaded file to the new file path
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path

# File uploader for audio files
uploaded_files = st.file_uploader("Choose an audio file", accept_multiple_files=True, type=['wav', 'mp3', 'pcm'])

for uploaded_file in uploaded_files:
    # Check if transcription is already cached
    if uploaded_file.name in st.session_state['transcribed_texts']:
        transcribed_text = st.session_state['transcribed_texts'][uploaded_file.name]
        text_area_placeholder = st.empty()
        text_area_placeholder.text_area(f"Transcribed Text for {uploaded_file.name}:", transcribed_text, height=300, disabled=True, key=f"transcribed_text_{uploaded_file.name}")
    else:
        # Display a placeholder text area indicating that transcription is in progress
        text_area_placeholder = st.empty()
        text_area_placeholder.text_area(f"Transcribing Text for {uploaded_file.name}:", "AI system working...", height=300, disabled=True)

        # Process and save the uploaded file
        file_path = save_uploaded_file(uploaded_file)

        # Transcribe the speech
        transcribed_text = transcribe_speech_from_file_continuous(file_path, SPEECH_KEY, SPEECH_REGION)
        st.session_state['transcribed_texts'][uploaded_file.name] = transcribed_text

        # Update the display with the transcribed text
        text_area_placeholder.text_area(f"Transcribed Text for {uploaded_file.name}:", transcribed_text, height=300, disabled=True, key=f"transcribed_text_{uploaded_file.name}")

    # Button for synthesizing speech
    if st.button('🔊 Synthesize Speech', key=f"synthesize_{uploaded_file.name}"):
        synthesize_speech(transcribed_text, SPEECH_KEY, SPEECH_REGION)

    st.markdown("---")  # Adds a separator line

# Function to remove a specific transcription from the history
def remove_transcription(file_name):
    if file_name in st.session_state['transcribed_texts']:
        del st.session_state['transcribed_texts'][file_name]
    
# Display download buttons for each transcribed file
for file_name, transcription in st.session_state['transcribed_texts'].items():
    # Add file name, transcription length, and transcription to the file text
    file_text = f"File Name: {file_name}\n"
    file_text += f"Transcription Length: {len(transcription)} tokens\n"
    file_text += f"Transcription:\n\n{transcription}\n"

    st.download_button(
        label=f"Download Transcription for {file_name}",
        data=file_text,
        file_name=f"transcription_{file_name}.txt",
        mime="text/plain",
        key=f"download_{file_name}"
    )



