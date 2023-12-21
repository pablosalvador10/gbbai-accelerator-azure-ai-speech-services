import asyncio
import base64
import os
import uuid
from datetime import datetime

import streamlit as st

from src.aoai_sdk.intent_azure_openai import generate_text_with_contextual_history

# Import your Azure AI Speech to Text function
from src.speech.speech_recognizer import recognize_from_microphone
from src.speech.text_to_speech import synthesize_speech
from utils.ml_logging import get_logger

# Set up logger and environment variables
logger = get_logger()
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")

# Define stop words and silence threshold
STOP_WORDS = ["goodbye", "exit", "stop", "see you later", "bye"]
SILENCE_THRESHOLD = 20  # in seconds

# Initialize session state for conversation history and real-time conversation
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = []
    st.session_state["real_time_conversation"] = ""
    st.session_state["run"] = False


# Function to convert image to base64
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def clear_conversation_history():
    """
    Clear the conversation history stored in the session state.
    """
    st.session_state["conversation_history"] = []


# Start/stop audio transmission
def start_listening(key, region):
    st.session_state["conversation_id"] = str(uuid.uuid4())
    st.session_state["conversation_start_time"] = datetime.now()
    logger.info(
        f"Starting listening with key: {key}, region: {region}, Conversation ID: {st.session_state['conversation_id']}, Start Time: {st.session_state['conversation_start_time'].isoformat()}"
    )
    response = "Hello, how can I help you?"
    st.session_state["run"] = True
    st.sidebar.markdown("#### Live Conversation:")
    with st.sidebar:
        st.write(f"🤖 AI System: {response}")
    synthesize_speech(response, SPEECH_KEY, SPEECH_REGION)
    asyncio.run(send_receive(key, region))


def stop_listening():
    st.session_state["run"] = False
    st.session_state["real_time_conversation"] = ""
    st.session_state["conversation_end_time"] = datetime.now()
    st.session_state["conversation_duration"] = (
        st.session_state["conversation_end_time"]
        - st.session_state["conversation_start_time"]
    ).total_seconds()
    download_conversation_history()


def download_conversation_history():
    if st.session_state["conversation_history"]:
        # Add conversation ID, start time, end time, and duration to the conversation history
        conversation_text = f"Conversation ID: {st.session_state['conversation_id']}\n"
        conversation_text += f"Conversation Start Time: {st.session_state['conversation_start_time'].isoformat()}\n"
        conversation_text += f"Conversation End Time: {st.session_state['conversation_end_time'].isoformat()}\n"
        conversation_text += f"Conversation Duration: {st.session_state['conversation_duration']} seconds\n\n"
        conversation_text += "Conversation:\n\n"
        conversation_text += "\n".join(st.session_state["conversation_history"])
        st.download_button(
            label="Download Conversation History",
            data=conversation_text,
            file_name=f"conversation_history_{st.session_state['conversation_id']}.txt",
            mime="text/plain",
            key="download_conversation_history",
        )


# Web user interface
st.markdown(
    f"""
    <h1 style="text-align:center;">
        🤖 Real-Time Conversational Agent
        <br>
        <span style="font-style:italic; font-size:0.5em;">powered by Azure AI services</span> <img src="data:image/png;base64,{get_image_base64('./utils/images/azure_logo.png')}" alt="logo" style="width:30px;height:30px;">
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

# Styling buttons with Streamlit columns
col1, col2, col3 = st.columns(3)
with col1:
    start_button = st.button(
        "Start Conversation",
        on_click=lambda: start_listening(SPEECH_KEY, SPEECH_REGION),
    )
with col2:
    stop_button = st.button("Stop Conversation", on_click=stop_listening)
with col3:
    clear_button = st.button("Clear History", on_click=clear_conversation_history)


# Main functionality with real-time updates
async def send_receive(key, region):
    last_speech_time = asyncio.get_event_loop().time()

    while st.session_state["run"]:
        try:
            prompt, _ = recognize_from_microphone(key, region)
            if prompt:
                last_speech_time = asyncio.get_event_loop().time()
                st.session_state["conversation_history"].append(f"User: {prompt}")
                with st.sidebar:
                    st.write(f"👤 User: {prompt}")

                if any(stop_word in prompt.lower() for stop_word in STOP_WORDS):
                    st.session_state["run"] = False
                    response = "Goodbye. I hope I was able to help you today."
                    synthesize_speech(response, SPEECH_KEY, SPEECH_REGION)
                    st.session_state["conversation_history"].append(
                        f"AI System: {response}"
                    )
                    with st.sidebar:
                        st.write(f"🤖 AI System: {response}")
                    stop_listening()
                    break

                response = generate_text_with_contextual_history(
                    [],
                    prompt,
                    deployment_name="foundational-canadaeast-gpt4",
                )
                if response:
                    synthesize_speech(response, SPEECH_KEY, SPEECH_REGION)
                    st.session_state["conversation_history"].append(
                        f"AI System: {response}"
                    )
                    with st.sidebar:
                        st.write(f"🤖 AI System: {response}")
                    last_speech_time = asyncio.get_event_loop().time()

            elif asyncio.get_event_loop().time() - last_speech_time > SILENCE_THRESHOLD:
                st.session_state["run"] = False
                response = (
                    f"No speech detected for over {SILENCE_THRESHOLD} seconds. Goodbye."
                )
                st.session_state["conversation_history"].append(
                    f"AI System: {response}"
                )
                stop_listening()
                break

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            st.session_state["run"] = False
            break

        await asyncio.sleep(0.1)


# Conversation history display
if not st.session_state["run"] and st.session_state["conversation_history"]:
    st.markdown("##### Conversation History:")
    chat_format = "\n".join(
        [
            "👤 " + line if "User:" in line else "🤖 " + line
            for line in st.session_state["conversation_history"]
        ]
    )
    st.text_area(
        "Chat",
        placeholder="Chat history will appear here once the conversation ends...",
        value=chat_format,
        height=300,
        disabled=True,
    )
