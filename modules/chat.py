import streamlit as st
from services.chat_handler import run_custom_chat


def show():
    # Custom CSS for better chat styling
    st.markdown("""
    <style>
    .user-message {
        text-align: right;
        margin: 8px 0;
    }
    .user-bubble {
        display: inline-block;
        background: #007bff;
        color: white;
        padding: 8px 12px;
        border-radius: 18px 18px 4px 18px;
        max-width: 70%;
        word-wrap: break-word;
        font-size: 14px;
    }
    .ai-message {
        text-align: left;
        margin: 8px 0;
    }
    .ai-bubble {
        display: inline-block;
        background: #e9ecef;
        color: #333;
        padding: 8px 12px;
        border-radius: 18px 18px 18px 4px;
        max-width: 70%;
        word-wrap: break-word;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("Conversational Chat Interface")

    # Configuration row
    col1, col2 = st.columns([3, 2])

    with col1:
        endpoint = st.text_input(
            "Endpoint",
            placeholder="http://localhost:11434/api/chat",
            key="chat_endpoint"
        )

    with col2:
        api_token = st.text_input(
            "API Token",
            type="password",
            placeholder="Enter API token if required",
            key="chat_token"
        )

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Chat display area
    st.markdown("Chat")

    # Create scrollable chat container
    chat_html = '<div class="chat-container" id="chat-container">'

    if st.session_state.chat_history:
        for speaker, text in st.session_state.chat_history:
            st.markdown(f"{speaker}: {text}")
    else:
        st.markdown("💬 Start a conversation...")

    # chat_html += '</div>'

    # Add auto-scroll script
    chat_html += '''
    <script>
    var container = document.getElementById("chat-container");
    container.scrollTop = container.scrollHeight;
    </script>
    '''

    st.markdown(chat_html, unsafe_allow_html=True)

    # Chat input at bottom
    user_input = st.chat_input("Type your message here...")

    # Handle message sending
    if user_input and endpoint:
        # Add user message
        st.session_state.chat_history.append(("You", user_input))

        # Generate response
        with st.spinner("Processing..."):
            try:
                reply = run_custom_chat(endpoint, user_input, api_token=api_token if api_token else None)
                st.session_state.chat_history.append(("AI", reply))
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.session_state.chat_history.append(("System", error_msg))
                st.error(error_msg)

        st.rerun()

    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()