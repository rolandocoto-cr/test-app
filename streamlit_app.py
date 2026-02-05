import streamlit as st
import requests

st.title("Cook Islands Māori TTS")

user_input = st.text_input("Enter your text:", value="Kia orana kōtou kātoatoa")

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'audio_bytes' not in st.session_state:
    st.session_state.audio_bytes = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None

# Button with dynamic text and disabled state
button_text = "Please wait..." if st.session_state.processing else "Process"
button_clicked = st.button(button_text, disabled=st.session_state.processing)

if button_clicked:
    # Clear previous results
    st.session_state.audio_bytes = None
    st.session_state.error_message = None
    st.session_state.processing = True
    st.rerun()

if st.session_state.processing:
    try:
        response = requests.post(
            "https://fastspeech2-cim-790340752928.us-east1.run.app/synthesize",
            json={"text": user_input},
            timeout=60
        )
        
        if response.ok:
            st.session_state.audio_bytes = response.content
        else:
            st.session_state.error_message = f"HTTP Error {response.status_code}: {response.reason}\nResponse body: {response.text}"
    except requests.exceptions.ConnectionError as e:
        st.session_state.error_message = f"Connection error: {e}"
    except requests.exceptions.Timeout as e:
        st.session_state.error_message = f"Request timed out: {e}"
    except Exception as e:
        st.session_state.error_message = f"Unexpected error: {type(e).__name__}: {e}"
    finally:
        st.session_state.processing = False
        st.rerun()

# Display results (persists after rerun)
if st.session_state.audio_bytes:
    st.success("Audio generated!")
    st.audio(st.session_state.audio_bytes, format='audio/wav')
    st.download_button(
        label="Download WAV",
        data=st.session_state.audio_bytes,
        file_name="output.wav",
        mime="audio/wav"
    )

if st.session_state.error_message:
    st.error(st.session_state.error_message)
