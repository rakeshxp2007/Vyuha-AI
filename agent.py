import os
from agno.models.openai import OpenAIChat
from agno.agent import Agent
from agno.team import Team
#from agno.tools.newspaper import NewspaperTools
from agno.tools.duckduckgo import DuckDuckGoTools
from knowledge_gs1 import knowledge_base
from agno.models.google.gemini import Gemini
import streamlit as st
from opik import track
from dotenv import load_dotenv
#from agno.tools.fal import FalTools
from sketch_tool import OpenAIDalleTool

#from agno.tools.nano_banana import NanoBananaTools

load_dotenv()


# creating a helper function to get instrctions for the agent
@track(name='load_instructions_gs1_sme')
def get_instruction(filename):
    try:
        file_path = os.path.join("instructions", filename)
        with open('instructions_for_smegs1.md','r') as f:
            return f.read()
    except FileNotFoundError:
        return "You are a UPSC GS-1 Subject Matter Expert."
    
@track(name='load_instructions_chief_examiner')   
def get_supervisor_instructions():
    try:
        with open("instructions_for_supervisor.md", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "You are the supervisor. Ensure answers are within words and strictly follow GS-1 syllabus."


@track(name="initialize_gs1_agent")
def get_gs1_agent():
    # We create a new instance of the model and agent every time this is called
    #brain = Gemini(id="gemini-2.0-flash-exp",thinking_level='high')
    #brain = Gemini(id="gemini-3-flash-preview", thinking_level='high')
    brain= OpenAIChat(id='gpt-4o')
    
    instructions = get_instruction('instructions_for_smegs1.md')

    # Initialize the Sketching Tool
    # sketch_tool = FalTools(
    #     api_key=os.getenv("FAL_KEY"),
    #     model="fal-ai/fast-lightning-sdxl", 
    # )

    sketch_tool = OpenAIDalleTool()

 
    return Agent(
        name='vhuya-sme-gs1',
        model=brain,
        knowledge=knowledge_base,
        search_knowledge=True,
        instructions=instructions,
        tools=[DuckDuckGoTools(),sketch_tool],
        markdown=True,
        debug_mode=True,
        add_history_to_context=True,
        add_knowledge_to_context=True
    )

# Prompt Generation Agent

@track(name='prompt_generator')
def get_visual_agent():
    return Agent(
        name='Visual-Architect',
        role='UPSC Diagram Speacialist',
        instructions=["You receive a UPSC question and a draft answer.",
            "Your ONLY task is to create a PROMPT for a pencil sketch by understanding the demand of the question and the drafted answer.",
            "Focus on geographic accuracy: Use keywords like 'cross-section', 'schematic', 'contour map'.",
            "Output ONLY the prompt string, nothing else."],
        model=OpenAIChat(id="gpt-4o"),
        markdown= True,
        debug_mode=True
    )

# Creating Supervisor
@track(name= "initialising_chief_examiner")
def get_supervisor_team():
    supervisor= Team(
        name= 'Answer Reviewer',
        members=[get_gs1_agent(), get_visual_agent()],
        id='answer_reviewer',
        show_members_responses=True,
        instructions=get_supervisor_instructions(),
        model=OpenAIChat(id='gpt-4o'),
        debug_mode=True
        
    )

    return supervisor

