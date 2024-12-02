import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
from typing import List, Dict
import time
from CoachingApp  import CoachingApp
# Load environment variables
load_dotenv()
from llm_config import system_prompt as SYSTEM_PROMPT
# Constants

def main():
    # Load system prompt from config    
    # Create and run the coaching app
    app = CoachingApp(SYSTEM_PROMPT)
    app.render_chat_interface()

if __name__ == "__main__":
    main()