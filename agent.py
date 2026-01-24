import os
from agno.models.openai import OpenAIChat
from agno.agent import Agent
#from agno.tools.newspaper import NewspaperTools
from agno.tools.duckduckgo import DuckDuckGoTools
from knowledge_gs1 import knowledge_base
from agno.models.google.gemini import Gemini
import streamlit as st
from opik import track
from dotenv import load_dotenv

load_dotenv()


# creating a helper function to get instrctions for the agent
@track(name='load_instructions')
def get_instruction(filename):
    try:
        file_path = os.path.join("instructions", filename)
        with open('instructions_for_smegs1.md','r') as f:
            return f.read()
    except FileNotFoundError:
        return "You are a UPSC GS-1 Subject Matter Expert."




@track(name="initialize_gs1_agent")
def get_gs1_agent():
    # We create a new instance of the model and agent every time this is called
    #brain = Gemini(id="gemini-2.0-flash-exp")
    #brain = Gemini(id="gemini-3-flash-preview", thinking_level='high')
    brain= OpenAIChat(id='gpt-4o')
    
    instructions = get_instruction('instructions_for_smegs1.md')
    
    return Agent(
        name='vhuya-sme-gs1',
        model=brain,
        knowledge=knowledge_base,
        search_knowledge=True,
        instructions=instructions,
        tools=[DuckDuckGoTools()],
        markdown=True,
        add_history_to_context=True,
        add_knowledge_to_context=True
    )

