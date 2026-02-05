import streamlit as st
import requests

st.title("Cook Islands Māori TTS")

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'audio_bytes' not in st.session_state:
    st.session_state.audio_bytes = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None
if 'user_text' not in st.session_state:
    st.session_state.user_text = "Kia orana kōtou kātoatoa"
if 'input_key' not in st.session_state:
    st.session_state.input_key = 0

# Callbacks for each character button
def add_char(char):
    st.session_state.user_text = st.session_state.user_text + char
    st.session_state.input_key += 1  # Change key to force refresh

# Callback when user types in the text box
def on_text_change():
    st.session_state.user_text = st.session_state[f"text_input_{st.session_state.input_key}"]

# Text input with dynamic key
st.text_input(
    "Enter your text:", 
    value=st.session_state.user_text,
    key=f"text_input_{st.session_state.input_key}",
    on_change=on_text_change
)

# Special character buttons in a horizontal row
st.caption("Insert special characters:")

special_chars = ['ā', 'ē', 'ī', 'ō', 'ū', 'ꞌ']
cols = st.columns(len(special_chars))

for idx, char in enumerate(special_chars):
    with cols[idx]:
        st.button(char, key=f"btn_{idx}", use_container_width=True, on_click=add_char, args=(char,))

# Spacer
st.write("")

# Button with dynamic text and disabled state
button_text = "Please wait..." if st.session_state.processing else "Generate audio"
button_clicked = st.button(button_text, disabled=st.session_state.processing)

if button_clicked:
    # Clear previous results
    st.session_state.audio_bytes = None
    st.session_state.error_message = None
    st.session_state.processing = True
    st.rerun()

if st.session_state.processing:
    try:
        # Get API URL from secrets
        api_url = st.secrets["API_URL"]
        
        response = requests.post(
            api_url,
            json={"text": st.session_state.user_text},
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
