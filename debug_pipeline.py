import os
import pandas as pd
import logging
import sys
from dotenv import load_dotenv

# Agno & Opik
from openai import OpenAI
from opik.integrations.openai import track_openai
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.chunking.fixed import FixedSizeChunking
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.lancedb import LanceDb
from agno.knowledge.reader.csv_reader import CSVReader

# --- 1. SETUP LOGGING ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

load_dotenv()

# --- 2. CREATE TINY TEST DATA ---
NCERT_PATH = './NCERT'
TEST_FILE = './NCERT/debug_test.csv'

def create_tiny_test_file():
    # Find any CSV and take just 10 rows
    for f in os.listdir(NCERT_PATH):
        if f.endswith('.csv') and 'debug' not in f:
            full_path = os.path.join(NCERT_PATH, f)
            print(f"Creating test file from {f}...")
            df = pd.read_csv(full_path).head(10) # ONLY 10 ROWS
            df.to_csv(TEST_FILE, index=False)
            return True
    return False

# --- 3. RUN PIPELINE ---
if __name__ == "__main__":
    if not create_tiny_test_file():
        print("No CSVs found to test.")
        exit()

    print("\n--- STARTING DEBUG RUN (10 Rows) ---")

    # A. Setup OpenAI without Opik first (to rule it out)
    # If this works, the issue was Opik. If this fails, the issue is Network/Agno.
    client = OpenAI() 
    # Uncomment next line ONLY after verifying it works without Opik
    # client = track_openai(client) 

    embedder = OpenAIEmbedder(
        id="text-embedding-3-small",
        openai_client=client
    )

    vector_db = LanceDb(
        uri='./lance_db/debug_test',
        embedder=embedder,
        table_name='debug_table'
    )

    chunking = FixedSizeChunking(chunk_size=1000, overlap=0)
    reader = CSVReader(chunking_strategy=chunking)

    knowledge_base = Knowledge(vector_db=vector_db)

    # B. Run Ingestion
    try:
        knowledge_base.add_content(
            path=TEST_FILE,
            reader=reader,
            upsert=True
        )
        print("\n--- SUCCESS! Pipeline is working. ---")
    except Exception as e:
        print(f"\n--- FAILED: {e} ---")
        logging.exception("Crash details:")