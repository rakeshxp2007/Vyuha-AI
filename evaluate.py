import os
import pandas as pd
import numpy as np
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

# Opik pulls OPIK_API_KEY from .env automatically. 
# We only pass the workspace here.
client = Opik(workspace=os.getenv("OPIK_WORKSPACE"))

# 2. FIX: Dataset Type Casting & NaN Handling
def get_benchmarking_dataset():
    dataset_name = "Vyuha-Benchmark-v1"
    try:
        return client.get_dataset(name=dataset_name)
    except Exception:
        dataset = client.create_dataset(name=dataset_name)
        df = pd.read_csv("llm_as_judge_ds.csv")
        
        # STRICTOR TYPE CASTING:
        # First fill NaNs with empty strings, then force everything to string type
        df = df.fillna("").astype(str) 
        
        dataset_items = df.to_dict(orient="records")
        dataset.insert(dataset_items)
        return dataset

# 3. FIX: Handling 'NoneType' and Printing Context
def evaluation_task(dataset_item):
    agent = get_gs1_agent()
    # Run the agent (evaluation must be non-streaming)
    response = agent.run(dataset_item["input"], stream=False)
    
    retrieved_context = []
    
    # GUARD: Using 'or []' ensures we iterate over a list even if Agno returns None
    for msg in (response.messages or []):
        if msg and hasattr(msg, 'role') and msg.role == "tool":
            retrieved_context.append(str(msg.content))
            
    # GUARD: 'references' is common in newer Agno versions for RAG
    if hasattr(response, 'references') and response.references:
        for ref in (response.references or []):
            retrieved_context.append(str(ref))

    # DEBUG: See exactly what NCERT chunks are being picked up
    print(f"\n--- Context for Question: {dataset_item['input'][:50]}... ---")
    print(retrieved_context if retrieved_context else "⚠️ No NCERT chunks retrieved!")

    return {
        "input": str(dataset_item["input"]),
        "output": str(response.content) if response.content else "No output",
        "reference": str(dataset_item["reference"]),
        "context": retrieved_context if retrieved_context else ["No context retrieved"]
    }

# 4. RUN EVALUATION
if __name__ == "__main__":
    dataset = get_benchmarking_dataset()
    
    metrics = [
        Hallucination(), LevenshteinRatio(), Moderation(), 
        AnswerRelevance(), ContextRecall(), ContextPrecision()
    ]

    print("🚀 Starting Vyuha-AI Evaluation...")
    evaluate(
        experiment_name="Vyuha-Benchmark-Run",
        dataset=dataset,
        task=evaluation_task,
        scoring_metrics=metrics
    )