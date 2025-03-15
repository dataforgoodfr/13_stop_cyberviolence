import streamlit as st

def initialize_session_state():
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'api_key_configured' not in st.session_state:
        st.session_state.api_key_configured = False