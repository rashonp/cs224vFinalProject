import os
from openai import OpenAI
import streamlit as st
from typing import List, Dict
import time
MODEL_NAME = "gpt-4"
MAX_RETRIES = 3
RETRY_DELAY = 2

class CoachingApp:
    def __init__(self, system_prompt: str):
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.system_prompt = system_prompt
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize or reset session state variables"""
        if 'messages' not in st.session_state:
            st.session_state['messages'] = []
        if 'conversation_count' not in st.session_state:
            st.session_state['conversation_count'] = 0
        if 'current_role' not in st.session_state:
            st.session_state['current_role'] = 'coach'
        if 'needs_initial_message' not in st.session_state:
            st.session_state['needs_initial_message'] = True

    def generate_response(self, messages: List[Dict[str, str]], retry_count: int = 0) -> str:
        """Generate response with error handling and retry logic"""
        try:
            stream = self.openai_client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                stream=True
            )
            
            response_placeholder = st.empty()
            full_response = ""
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            return full_response

        except Exception as e:
            if retry_count < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                return self.generate_response(messages, retry_count + 1)
            else:
                st.error(f"Error generating response: {str(e)}")
                return "I apologize, but I'm having trouble responding right now. Please try again."

    def update_conversation_count(self):
        """Update conversation count and handle role switching"""
        st.session_state['conversation_count'] += 1
        if st.session_state['conversation_count'] >= 6:  # 3 exchanges (user + assistant responses)
            st.session_state['conversation_count'] = 0
            st.session_state['current_role'] = 'coach'
            return True
        return False

    def render_chat_interface(self):
        """Render the main chat interface"""
        st.title("Noora -- Being Asked to Give Advice Module")
        
        # Add session controls
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("New Session"):
                self.reset_session()

        # Initialize first message if needed
        if st.session_state['needs_initial_message']:
            initial_messages = [{'role': 'system', 'content': self.system_prompt}]
            response = self.generate_response(initial_messages)
            st.session_state['messages'].append({'role': 'assistant', 'content': response})
            st.session_state['needs_initial_message'] = False

        # Display chat history
        self.display_chat_history()

        # Handle user input
        self.handle_user_input()

    def display_chat_history(self):
        """Display the chat history"""
        for message in st.session_state['messages']:
            if message['role'] != 'system':
                with st.chat_message(message['role']):
                    st.markdown(message['content'])

    def handle_user_input(self):
        """Handle user input and generate responses"""
        if prompt := st.chat_input("You:"):
            # Add user message
            st.session_state['messages'].append({'role': 'user', 'content': prompt})
            with st.chat_message('user'):
                st.markdown(prompt)

            # Generate and display assistant response
            with st.chat_message('assistant'):
                full_response = self.generate_response(st.session_state['messages'])
                st.session_state['messages'].append({'role': 'assistant', 'content': full_response})

            # Check if we need to switch scenarios
            if self.update_conversation_count():
                st.info("Moving to next scenario...")
                time.sleep(2)
                st.rerun()

    def reset_session(self):
        """Reset the session state"""
        st.session_state['messages'] = []
        st.session_state['conversation_count'] = 0
        st.session_state['current_role'] = 'coach'
        st.session_state['needs_initial_message'] = True
        st.rerun()
