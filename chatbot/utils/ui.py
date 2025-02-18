import streamlit as st

def main_sidebar():

    with st.sidebar:
        st.header("LLM Configuration")
                    
        # Temperature slider
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Higher values make output more random, lower more deterministic"
        )
        
        # Max tokens slider
        max_tokens = st.slider(
            "Max Tokens",
            min_value=100,
            max_value=4000,
            value=1000,
            step=100,
            help="Maximum number of tokens to generate"
        )
            
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

    return temperature, max_tokens