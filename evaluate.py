import os
import pandas as pd
import json
from dotenv import load_dotenv
from opik import Opik
from opik.evaluation import evaluate
from opik.evaluation.metrics import (
    Hallucination, LevenshteinRatio, Moderation, 
    AnswerRelevance, ContextRecall, ContextPrecision
)
from agent import get_gs1_agent 

# 1. LOAD ENVIRONMENT VARIABLES
load_dotenv() 

# Initialize Opik Client
client = Opik(workspace=os.getenv("OPIK_WORKSPACE"))

# 2. DATASET LOADER (With the "NaN" Fix)
def get_benchmarking_dataset():
    dataset_name = "Vyuha-Benchmark-GS1-v2"
    
    # 1. DELETE EXISTING (Clean Slate)
    try:
        client.delete_dataset(name=dataset_name)
        print(f"🗑️ Deleted old version of {dataset_name}")
    except:
        pass # It didn't exist, which is fine

    # 2. CREATE FRESH
    print(f"🆕 Creating fresh dataset: {dataset_name}")
    dataset = client.create_dataset(name=dataset_name)
    
    # 3. READ & INSERT
    try:
        df = pd.read_csv("llm_as_judge_ds.csv",encoding="latin1")
        
        # 1. Force all column names to be strings (Fixes 'Hashable' error)
        df.columns = df.columns.astype(str)
        
        # 2. Force all data to be strings (Fixes NaN/Float errors)
        df = df.fillna("").astype(str)
        
        # 3. Explicitly type hint the variable (Optional, helps Pylance)
        from typing import List, Dict, Any
        dataset_items: List[Dict[str, Any]] = df.to_dict(orient="records")
        
        dataset.insert(dataset_items)
        print(f"✅ Successfully inserted {len(dataset_items)} items from CSV.")
        
    except FileNotFoundError:
        print("❌ CRITICAL ERROR: 'llm_as_judge_ds.csv' not found in this folder.")
        raise
        
    return dataset

# 3. THE EXAM TASK (Agent runs here)
def evaluation_task(dataset_item):
    # Initialize a fresh agent for each question
    agent = get_gs1_agent()
    
    # Run the Agent (Non-streaming for evaluation)
    # We use the prompt from the CSV 'input' column
    response = agent.run(dataset_item["input"], stream=False)
    
    # --- CONTEXT EXTRACTION ---
    # We need to find what the agent "read" to check for Hallucinations
    retrieved_context = []
    
    # 1. Check for Tool Messages (Search Results/Knowledge Base)
    if hasattr(response, 'messages'):
        for msg in (response.messages or []):
            if hasattr(msg, 'role') and msg.role == "tool":
                # Clean up tool output to be string
                retrieved_context.append(str(msg.content))
                
    # 2. Check for Direct References (if available in your Agno version)
    if hasattr(response, 'references'):
        for ref in (response.references or []):
            retrieved_context.append(str(ref))
            
    # Default to "No Context" if nothing found (prevents metric crash)
    final_context = retrieved_context if retrieved_context else ["No external context used"]

    return {
        "input": str(dataset_item["input"]),
        "output": str(response.content) if response.content else "Error: No Output",
        "reference": str(dataset_item["reference"]), # The "Model Answer" from your CSV
        "context": final_context
    }

# 4. RUN THE BENCHMARK
if __name__ == "__main__":
    # Get the dataset
    dataset = get_benchmarking_dataset()
    
    # Define the Metrics (The "Grading Rubric")
    metrics = [
        Hallucination(),       # Is it making things up?
        AnswerRelevance(),     # Did it answer the specific question?
        LevenshteinRatio(),    # How close is the text to your reference answer?
        Moderation(),          # Is the content safe?
        ContextRecall(),       # Did we find the right facts in the search?
        ContextPrecision()     # Is the relevant info ranked high?

    ]

    print("\n🚀 Starting Vyuha-AI Evaluation Run...")
    print("This may take a few minutes depending on the number of questions...\n")
    
    evaluate(
        experiment_name="Vyuha-GS1-Experiment-06", # Change this name for subsequent runs (02, 03...)
        dataset=dataset,
        task=evaluation_task,
        scoring_metrics=metrics,
        scoring_key_mapping={'expected_output': 'reference'},
        verbose=True
        )
    
    print("\n✅ Evaluation Complete! Check your Opik Dashboard.")