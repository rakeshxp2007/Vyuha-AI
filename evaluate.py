import os
import pandas as pd
from opik import Opik, track
from opik.evaluation import evaluate
from opik.evaluation.metrics import (
    Hallucination, 
    AnswerRelevance, 
    ContextRecall, 
    ContextPrecision
)
from datasets import Dataset # HuggingFace datasets, useful helper

# Import your actual Agent logic
from agent import get_gs1_agent

def get_dataset_from_csv(client, csv_path="llm_as_judge_ds.csv"):
    dataset_name = "UPSC-Toppers-Benchmark"
    
    # 1. Read CSV
    try:
        df = pd.read_csv(csv_path)
        print(f"📖 Loaded {len(df)} rows from {csv_path}")
    except FileNotFoundError:
        print("❌ CSV not found!")
        return None
    
    # 2. Check/Create Dataset in Opik
    try:
        dataset = client.get_dataset(name=dataset_name)
        # Optional: If you want to overwrite/update, you might delete it first
        # client.delete_dataset(name=dataset_name) 
        print(f"✅ Found existing dataset in Opik: {dataset_name}")
    except:
        print(f"wb Creating new dataset: {dataset_name}...")
        dataset = client.create_dataset(name=dataset_name)
        
        dataset.insert(df.to_dict(orient="records"))


# --- 1. PREPARE THE DATASET ---
# We create a small "Golden Set" of UPSC Q&A pairs.
def get_or_create_dataset(client):
    dataset_name = "Vyuha-GS1-Golden-Set"
    
    # Check if exists, otherwise create
    try:
        dataset = client.get_dataset(name=dataset_name)
        print(f"✅ Found existing dataset: {dataset_name}")
    except:
        print(f"⚠️ Dataset not found. Creating {dataset_name}...")
        dataset = client.create_dataset(name=dataset_name)
        
        # Add sample items (Question + Expert Reference Answer)
        dataset.insert([
            {
                "input": "Discuss the impact of British rule on Indian handicrafts.",
                "reference": "British rule led to de-industrialization due to discriminatory tariffs, loss of royal patronage, and competition from machine-made goods.",
                # Context is usually what the RAG retrieves. For the 'reference' (ground truth),
                # we can leave context empty or provide the 'ideal' text snippet.
                "expected_context": ["The decline of handicrafts was a result of colonial policies..."] 
            },
            {
                "input": "What are the locational factors for the sugar industry?",
                "reference": "Sugar industry is raw-material oriented. Key factors: proximity to sugarcane fields (weight-losing crop), humidity (for sucrose content), and transport infrastructure.",
                "expected_context": ["Sugarcane is a weight-losing crop...", "Sugar factories are located near fields..."]
            }
        ])
    return dataset

# --- 2. THE TASK (Connecting Agent to Eval) ---
def evaluation_task(item):
    agent = get_gs1_agent()
    
    # Run agent
    response = agent.run(item["input"], stream=False)
    
    # 1. Capture Answer
    actual_output = response.content
    
    # 2. Capture Retrieved Context (The Fix)
    retrieved_context = []
    
    # CHECK 1: Knowledge Base Retrieval (RAG)
    # Agno stores retrieved references in 'response.context'
    if hasattr(response, 'context') and response.context:
        # response.context is usually a list of MessageContext objects or dicts
        for ctx in response.context:
            if hasattr(ctx, 'content'):
                retrieved_context.append(ctx.content)
            elif isinstance(ctx, dict) and 'content' in ctx:
                retrieved_context.append(ctx['content'])
            else:
                retrieved_context.append(str(ctx))
                
    # CHECK 2: Tool Outputs (Search Results)
    # If the agent used DuckDuckGo, the results are in the message history as tool outputs
    if not retrieved_context and hasattr(response, 'messages'):
        for msg in response.messages:
            if msg.role == "tool" and msg.content:
                retrieved_context.append(msg.content)

    # Fallback
    if not retrieved_context:
        retrieved_context = ["No context retrieved"]

    return {
        **item,
        "output": actual_output,
        "context": retrieved_context
    }

# --- 3. RUN EVALUATION ---
if __name__ == "__main__":
    client = Opik()
    dataset = get_or_create_dataset(client)
    
    # Define Metrics (LLM as a Judge)
    # Note: These will call an LLM (usually GPT-4) to grade your agent.
    metrics = [
        Hallucination(),        # Does output match context?
        AnswerRelevance(),      # Does output answer the input?
        ContextRecall(),        # Did we retrieve the right info?
        ContextPrecision()      # Was the retrieved info mostly useful?
    ]
    
    print("🚀 Starting Vyuha-AI Evaluation...")
    eval_results = evaluate(
        experiment_name="Vyuha-GS1-Experiment-v1",
        dataset=dataset,
        task=evaluation_task,
        scoring_metrics=metrics
    )
    
    print("✅ Evaluation Done! View results on Comet.com")