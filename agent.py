import os
from dotenv import load_dotenv

from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.agent import Agent
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from knowledge_gs1 import knowledge_base
from opik import track

load_dotenv()



# --- 2. INSTRUCTION LOADERS ---

@track(name='load_instructions_gs1_sme')
def get_instruction(filename):
    """Specific loader for SME Instructions"""
    try:
        file_path = os.path.join("instructions", filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "You are a UPSC GS-1 Subject Matter Expert."
    
@track(name='load_instructions_chief_examiner')   
def get_supervisor_instructions():
    """Specific loader for Supervisor Instructions"""
    try:
        # Assumes the file is in the root or instructions folder
        # Adjust path if it's inside 'instructions/' 
        path = os.path.join("instructions", "instructions_for_supervisor.md")
        if not os.path.exists(path):
             path = "instructions_for_supervisor.md" # Fallback to root
             
        with open(path, "r", encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "You are the supervisor. Ensure answers are within word limits and strictly follow GS-1 syllabus."

# -- THE AGENTS ---

@track(name="initialize_gs1_agent")
def get_gs1_agent():
    #brain = Gemini(id="gemini-2.0-flash")
    #brain = Gemini(id="gemini-2.5-flash")    
    brain = Gemini(id="gemini-3-flash-preview", thinking_level='low')
    #brain= OpenAIChat(id='gpt-4o')
    
    # Initialize the Sketching Tool
    # sketch_tool = FalTools(
    #     api_key=os.getenv("FAL_KEY"),s
    #     model="fal-ai/fast-lightning-sdxl", 
    # )

    return Agent(
        name='vhuya-sme-gs1',
        role="UPSC GS-1 Subject Matter Expert",
        model=brain,
        knowledge=knowledge_base,
        search_knowledge=True,
        instructions=get_instruction('instructions_for_smegs1.md'),
        tools=[DuckDuckGoTools()],
        markdown=True,
        debug_mode=True        
    )


# Creating Supervisor
@track(name= "initialising_chief_examiner")
def get_supervisor_team():
    sme = get_gs1_agent()
        
    # Load specific Supervisor instructions
    supervisor_instructions = get_supervisor_instructions()

    return Team(
        name='Chief-Examiner',
        role="UPSC Supervisor",
        model=Gemini(id="gemini-3-flash-preview", thinking_level='low'),        
        members=[sme],        
        instructions=supervisor_instructions,
        markdown=True,
        debug_mode=True
    )

