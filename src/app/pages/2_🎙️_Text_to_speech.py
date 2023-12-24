import base64
import os
import uuid
from datetime import datetime

import streamlit as st

from src.aoai.intent_azure_openai import AzureOpenAIAssistant
from src.speech.speech_to_text import transcribe_speech_from_file_continuous
from src.speech.text_to_speech import synthesize_speech
from utils.ml_logging import get_logger

# Set up logger and environment variables
logger = get_logger()
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")

# Initialize session state variables
if "transcribed_texts" not in st.session_state:
    st.session_state["transcribed_texts"] = {}
if "display_files" not in st.session_state:
    st.session_state["display_files"] = {}
if "clear_flag" not in st.session_state:
    st.session_state["clear_flag"] = {}
if "az_aoai" not in st.session_state:
    st.session_state["az_aoai"] = AzureOpenAIAssistant()

def get_image_base64(image_path: str) -> str:
    """
    Convert an image to a base64 encoded string.

    :param image_path: Path to the image file.
    :return: Base64 encoded string of the image.
    """
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def transcribe_with_progress(
    file_path: str, file_name: str, key: str, region: str
) -> str:
    """
    Transcribe speech from a file with a progress indicator.

    :param file_path: Path to the audio file.
    :param key: API key for the speech service.
    :param region: Region for the speech service.
    :return: Transcribed text.
    """
    with st.spinner(f"🤖 Transcribing {file_name}... Please wait."):
        transcribed_text = transcribe_speech_from_file_continuous(
            file_path, key, region
        )
    return transcribed_text


def summarize(text: str) -> str:
    """
    Summarize the provided text and extract its intent.

    :param text: The text to be summarized.
    :return: Summarized text and its intent.
    """
    with st.spinner(f"🤖 Summarizing and extracting intent from the text... Please wait."):
        response = st.session_state["az_aoai"].summarize_and_classify_intent(text=text)
    return response


def clear_filename_history(file_name: str):
    """
    Clear the transcription and display state for a specific file.

    :param file_name: Name of the file to clear from session state.
    """
    st.session_state["transcribed_texts"].pop(file_name, None)
    st.session_state["display_files"].pop(file_name, None)
    st.session_state["clear_flag"][file_name] = True


def save_uploaded_file(uploaded_file) -> str:
    """
    Save an uploaded file to a specified directory.

    :param uploaded_file: Streamlit UploadedFile object.
    :return: Path to the saved file.
    """
    upload_directory = os.path.join("src", "app", "uploads")
    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)

    st.session_state["conversation_id"] = str(uuid.uuid4())
    st.session_state["conversation_start_time"] = datetime.now()
    date_str = st.session_state["conversation_start_time"].strftime("%Y%m%d")

    subdirectory = os.path.join(
        upload_directory, f"{st.session_state['conversation_id']}_{date_str}"
    )
    if not os.path.exists(subdirectory):
        os.makedirs(subdirectory)

    file_path = os.path.join(subdirectory, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


# UI setup
st.markdown(
    f"""
    <h1 style="text-align:center;">
        🎙️ Speech to Text hub!
        <br>
        <span style="font-style:italic; font-size:0.5em;">powered by Azure AI services</span>
        <img src="data:image/png;base64,{get_image_base64('./utils/images/azure_logo.png')}" alt="logo" style="width:30px;height:30px;">
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
    return st.session_state["transcribed_texts"].get(file_name, "")


def clear_conversation_history():
    """
    Clear the conversation history stored in the session state.
    """
    st.session_state["conversation_history"] = []


def reset_application():
    """
    Reset the application state, clearing all cached data and files.
    """
    st.session_state["transcribed_texts"] = {}
    st.session_state["display_files"] = {}
    st.session_state["clear_flag"] = {}


def clear_filename_history(file_name):
    st.session_state["transcribed_texts"].pop(file_name, None)
    st.session_state["display_files"].pop(file_name, None)
    st.session_state["clear_flag"][file_name] = True  # Set flag to indicate clearing


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
    subdirectory = os.path.join(
        upload_directory, f"{st.session_state['conversation_id']}_{date_str}"
    )
    if not os.path.exists(subdirectory):
        os.makedirs(subdirectory)

    # Create a file path
    file_path = os.path.join(subdirectory, uploaded_file.name)

    # Write the uploaded file to the new file path
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


# File uploader for audio files
uploaded_files = st.file_uploader(
    "Choose an audio file", accept_multiple_files=True, type=["wav", "mp3", "pcm"]
)

for uploaded_file in uploaded_files:
    file_name = uploaded_file.name
    st.session_state["display_files"][file_name] = True

    if file_name not in st.session_state["transcribed_texts"]:
        file_path = save_uploaded_file(uploaded_file)
        transcribed_text = transcribe_with_progress(
            file_path, file_name, SPEECH_KEY, SPEECH_REGION
        )
        st.session_state["transcribed_texts"][file_name] = transcribed_text

    if st.session_state["display_files"].get(file_name):
        if st.session_state["clear_flag"].get(file_name):
            st.session_state["clear_flag"][file_name] = False
        else:
            text_display = st.session_state["transcribed_texts"].get(file_name, "")
            st.text_area(
                f"Transcribed Text for {file_name}:",
                text_display,
                height=300,
                disabled=True,
                key=f"transcribed_text_{file_name}",
            )

        col1, col2, col3 = st.columns(3)
        if col1.button("🔊 Generate Speech", key=f"synthesize_{file_name}"):
            synthesize_speech(text_display, SPEECH_KEY, SPEECH_REGION)
        if col2.button("📝 Summarize Text", key=f"summarize_{file_name}"):
            text = summarize(st.session_state["transcribed_texts"][file_name])
            st.text_area(
                f"Summarized Text for {file_name}:",
                text,
                height=100,
                disabled=True,
                key=f"summarized_text_{file_name}",
            )
        if col3.button("🗑️ Clear & Delete Data", key=f"clear_{file_name}"):
            clear_filename_history(file_name)

        st.markdown("---")

# Reset button
if st.button("🔄 Reset Application"):
    reset_application()

# Display download buttons for each transcribed file
for file_name, transcription in st.session_state["transcribed_texts"].items():
    # Add file name, transcription length, and transcription to the file text
    if st.session_state["display_files"].get(file_name, False):
        file_text = f"File Name: {file_name}\n"
        file_text += f"Transcription Length: {len(transcription)} tokens\n"
        file_text += f"Transcription:\n\n{transcription}\n"

        # Only display the download button if the file exists in the session state
        st.download_button(
            label=f"Download Transcription for {file_name}",
            data=file_text,
            file_name=f"transcription_{file_name}.txt",
            mime="text/plain",
            key=f"download_{file_name}",
        )
