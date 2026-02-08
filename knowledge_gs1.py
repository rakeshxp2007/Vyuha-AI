import os
import time
import hashlib
from tqdm import tqdm
from dotenv import load_dotenv

# --- Native Opik Imports  ---
from openai import OpenAI
import opik 
from opik.integrations.openai import track_openai

# --- Agno Imports ---
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.lancedb import LanceDb
#from agno.knowledge.chunking.fixed import FixedSizeChunking
from agno.knowledge.document import Document
from dataset_preprocessor import download_dataset, create_document, book_list

load_dotenv()


# --- Configuration ---
NCERT_PATH = './NCERT'
VECTOR_PATH = './lance_db/GS1'
BATCH_SIZE = 50
SLEEP_TIME = 1.5

os.environ["OPIK_PROJECT_NAME"] = "Vyuha-AI"
opik.configure(use_local=False)
client = OpenAI()
tracked_client = track_openai(client)


embedder = OpenAIEmbedder(
    id='text-embedding-3-large',
    openai_client=tracked_client,
    dimensions=3072
)

# Experimenting: from fixed size to metadata based chunking
# chunking_strategy = FixedSizeChunking(
#     chunk_size=2000,
#     overlap=0
#     )

vector_db = LanceDb(
    uri= VECTOR_PATH,
    embedder=embedder,
    table_name='GS1'
)

# creating the knowledgebase wrapper to be imported by agent.py later
knowledge_base = Knowledge(
    name= 'GS1_Knowledge_Base',
    description='class 11 & 12 NCERT history and Geography books embeddings',
    vector_db=vector_db
)

# --- NEW HELPER FUNCTION ---
def get_content_hash(text: str) -> str:
    """Generates a unique MD5 hash for the text content."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


# --- Main Ingestion Logic ---
@opik.track(name='Ingest NCERT')
def main():
    # 1. Verify Dataset
    if not os.path.exists(NCERT_PATH) or not os.listdir(NCERT_PATH):
        print("NCERT directory empty. Starting download...")
        download_dataset(base_path=NCERT_PATH, book_list=book_list)

    # 2. Load documents into memory (Returns Dictionary List)
    print("Reading and formatting documents...")
    all_doc_data = create_document(base_path=NCERT_PATH) 
    total_docs = len(all_doc_data)
    print(f"Loaded {total_docs} rows to process.")

    if total_docs == 0:
        print("No documents found to process. Exiting.")
        return

    # 3. Initialize/Reset Vector DB table
    # This creates the table with the schema from the embedder
    vector_db.create()

    # 4. Batch Processing Loop
    for i in tqdm(range(0, total_docs, BATCH_SIZE), desc="Processing Batches"):
        batch_data = all_doc_data[i : i + BATCH_SIZE]
        
        batch_documents = []
        batch_content_str = "" # Accumulator for the batch hash

        for item in batch_data:
            # Create Document using the pre-processed dictionary
            doc = Document(
                content=item['content'],
                meta_data=item['metadata'] # Passing the dictionary directly
            )
            
            # Generate unique ID based on content to prevent duplicates
            doc.id = get_content_hash(doc.content)
            
            batch_documents.append(doc)
            
            # Accumulate content for batch integrity check
            batch_content_str += doc.content

        # Calculate Batch Hash (Required by LanceDB upsert)
        batch_hash = get_content_hash(batch_content_str)

        try:
            # DIRECT UPSERT (No Chunking)
            vector_db.upsert(
                documents=batch_documents,
                content_hash=batch_hash 
            )
            
        except Exception as e:
            print(f"⚠️ Error in batch {i}: {e}")
            time.sleep(10) # Backoff on error
            continue

        # Politeness pause to avoid OpenAI Rate Limits
        time.sleep(SLEEP_TIME)

    print("\n\nSUCCESS! Knowledge Base populated safely.")
    
    # Force logs to send before closing
    opik.flush_tracker()

    
if __name__ == "__main__":
    main()