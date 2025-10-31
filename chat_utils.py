import streamlit as st

def initialize_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! Ask me anything about international football from 1872 to present."
            }
        ]

def display_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
def handle_user_input(openai_api_key: str, query_graph_func, chain):
    if prompt := st.chat_input("Enter your question about international football from 1872 to present:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        if openai_api_key:
            with st.spinner("Thinking..."):
                try:
                    response = query_graph_func(chain, prompt)
                except Exception as e:
                    st.error(f"Error: {e}")
                    response = f"Sorry, I encountered an error: {e}"
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            st.error("Please set your OpenAI API key in the sidebar.")