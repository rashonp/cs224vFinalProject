import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
from llm_config import system_prompt

load_dotenv()
openAI_client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

system_message = {
    'role': 'system',
    'content': system_prompt
}

# Set up Streamlit app
st.title("Noora -- Being Asked to Give Advice Module")

# Initialize session state to store messages
if 'messages' not in st.session_state:
    st.session_state['messages'] = [system_message]

    # Query the model for the initial assistant response
    with st.spinner("Generating initial assistant message..."):
        stream = openAI_client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state['messages'],
            stream=True
        )
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content


        # Add the assistant's response to the session state
        st.session_state['messages'].append({'role': 'assistant', 'content': full_response})

# Display previous messages
for message in st.session_state['messages']:
    if message['role'] != 'system':  # Skip displaying the system message
        with st.chat_message(message['role']):
            st.markdown(message['content'])

# Get user input
if prompt := st.chat_input("You:"):
    # Add user message to session state
    st.session_state['messages'].append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    # Generate response from ChatGPT
    with st.chat_message('assistant'):
        response_placeholder = st.empty()
        full_response = ""
        stream = openAI_client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state['messages'],
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(full_response + "▌")
        response_placeholder.markdown(full_response)
    # Add assistant response to session state
    st.session_state['messages'].append({'role': 'assistant', 'content': full_response})
