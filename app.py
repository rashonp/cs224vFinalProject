# app.py

import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
from llm_config import system_prompt as being_asked_advice
load_dotenv()
openAI_client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Define available modules
MODULES = {
    "Being Asked to Give Advice": "Practice giving advice in various scenarios",
    "Asking for Advice": "Practice asking for advice effectively",
    "Small Talk": "Practice engaging in casual conversation",
    "Difficult Conversations": "Practice handling challenging discussions",
    "Professional Communication": "Practice workplace communication"
}

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'selected_module' not in st.session_state:
    st.session_state['selected_module'] = None
if 'module_initialized' not in st.session_state:
    st.session_state['module_initialized'] = False

def initialize_module(module_name):
    """Initialize the selected module"""
    system_prompt = None
    if module_name == "Being Asked to Give Advice":
            system_prompt = being_asked_advice
    elif module_name == "Professional Communication":
            system_prompt = "ROyaaaaal Rumble"
    system_message = {
        'role': 'system',
        'content': system_prompt  # You might want to modify this based on the selected module
    }
    st.session_state['messages'] = [system_message]
    st.session_state['module_initialized'] = True
    
    # Generate initial message
    with st.spinner("Initializing module..."):
        stream = openAI_client.chat.completions.create(
            model="gpt-4",
            messages=st.session_state['messages'],
            stream=True
        )
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
        
        st.session_state['messages'].append({'role': 'assistant', 'content': full_response})

def reset_session():
    """Reset the session state"""
    st.session_state['messages'] = []
    st.session_state['module_initialized'] = False

# Main app interface
st.title("Noora - Social Skills Training")

# Module selection sidebar
with st.sidebar:
    st.header("Module Selection")
    for module, description in MODULES.items():
        if st.button(
            module,
            key=f"btn_{module}",
            help=description,
            type="primary" if st.session_state.get('selected_module') == module else "secondary"
        ):
            if st.session_state.get('selected_module') != module:
                st.session_state['selected_module'] = module
                reset_session()
                st.rerun()

    if st.session_state.get('selected_module'):
        st.divider()
        if st.button("Reset Session"):
            reset_session()
            st.rerun()

# Display selected module interface
if st.session_state.get('selected_module'):
    st.header(f"Module: {st.session_state['selected_module']}")
    
    # Initialize module if needed
    if not st.session_state['module_initialized']:
        initialize_module(st.session_state['selected_module'])
    
    # Display chat history
    for message in st.session_state['messages']:
        if message['role'] != 'system':
            with st.chat_message(message['role']):
                st.markdown(message['content'])

    # Handle user input
    if prompt := st.chat_input("You:"):
        # Add user message
        st.session_state['messages'].append({'role': 'user', 'content': prompt})
        with st.chat_message('user'):
            st.markdown(prompt)

        # Generate response
        with st.chat_message('assistant'):
            response_placeholder = st.empty()
            full_response = ""
            stream = openAI_client.chat.completions.create(
                model="gpt-4",
                messages=st.session_state['messages'],
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
            st.session_state['messages'].append({'role': 'assistant', 'content': full_response})
else:
    st.info("👈 Please select a module from the sidebar to begin.")