# Configure the SDK
import os
from dotenv import load_dotenv
load_dotenv()

import opik
from opik_optimizer import (
    ChatPrompt,
    MetaPromptOptimizer,
)
from opik.evaluation.metrics import LevenshteinRatio

# Define the prompt to optimize
prompt = ChatPrompt(
    system="Answer the question.",
    user="{question}", # This must match dataset field
)

# Get the dataset to evaluate the prompt on
client = opik.Opik()
dataset = client.get_dataset(name="llm_as_judge_ds")

# Define the metric to evaluate the prompt on
def levenshtein_ratio(dataset_item, llm_output):
    metric = LevenshteinRatio()
    return metric.score(
        reference=dataset_item["answer"], # This must match dataset field
        output=llm_output,
    )

# Run the optimization
optimizer = MetaPromptOptimizer(
    model="openai/gpt-4o-mini",  # Task model (LiteLLM name)
    n_threads=8,
    enable_context=True,
    seed=42,
    model_parameters= {'temperature':0.0}
   
)

result = optimizer.optimize_prompt(
    prompt=prompt,
    dataset=dataset,
    metric=levenshtein_ratio,
    n_samples=10,
)

result.display()
# Optimizer metadata (prompt, tools, version) is logged automatically.
