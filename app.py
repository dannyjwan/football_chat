import streamlit as st
from graph_utils import initialize_resources, query_graph
from chat_utils import initialize_chat_history, display_chat_history, handle_user_input
st.title("International Football Knowledge Graph")
with st.sidebar:
    openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")
    st.warning("Please enter your OpenAI API Key to use the chatbot.")

if openai_api_key:
    with st.spinner("Initializing resources..."):
        graph, chain = initialize_resources(openai_api_key)
        st.success("Resources initialized successfully.")
    # Initialize chat history
    initialize_chat_history()
    display_chat_history()
    # Handle user input
    handle_user_input(openai_api_key, query_graph, chain)
    