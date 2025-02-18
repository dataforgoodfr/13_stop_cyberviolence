import streamlit as st
from utils.llm import complete_chat
from utils.ui import main_sidebar
from utils.utils import initialize_session_state


def main():
    st.title("✊🏼 STOP Cyberviolence")

    initialize_session_state()
    temperature, max_tokens = main_sidebar()
    # Sidebar for configuration
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
    
    # Display chat messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Chat input
    if prompt := st.chat_input("Enter your message"):

        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = complete_chat(prompt, temperature, max_tokens)
                st.markdown(answer)
                
                # Add assistant message to history
                st.session_state.messages.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main()