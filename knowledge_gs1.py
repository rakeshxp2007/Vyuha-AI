import os
import time
import hashlib
from tqdm import tqdm
from dotenv import load_dotenv

# --- 1. Native Opik Imports (Reliable) ---
from openai import OpenAI
import opik 
from opik.integrations.openai import track_openai

# --- Agno Imports ---
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.lancedb import LanceDb
from agno.knowledge.chunking.fixed import FixedSizeChunking
from agno.knowledge.document import Document
from dataset_preprocessor import download_dataset, create_document, book_list

load_dotenv()


# --- Configuration ---
NCERT_PATH = './NCERT'
VECTOR_PATH = './lance_db/GS1'
BATCH_SIZE = 50
SLEEP_TIME = 2.0

os.environ["OPIK_PROJECT_NAME"] = "Vyuha-AI"
opik.configure(use_local=False)
client = OpenAI()
tracked_client = track_openai(client)


embedder = OpenAIEmbedder(
    id='text-embedding-3-small',
    openai_client=tracked_client
)

chunking_strategy = FixedSizeChunking(
    chunk_size=2000,
    overlap=0
    )

vector_db = LanceDb(
    uri= VECTOR_PATH,
    embedder=embedder,
    table_name='GS1'
)

# creating the knowledgebase 
knowledge_base = Knowledge(
    name= 'GS1_Knowledge_Base',
    description='class 11 & 12 NCERT history and Geography books embeddings',
    vector_db=vector_db
)

# --- NEW HELPER FUNCTION ---
def get_content_hash(text: str) -> str:
    """Generates a unique MD5 hash for the text content."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


# Creating a helper function to run batches 

@opik.track(name="Process Batch")
def process_single_batch(i, batch_texts, vector_db, chunking_strategy):
    """Handles processing and uploading of a single batch with Opik tracking."""
    raw_documents = [Document(content=text) for text in batch_texts]
    final_chunked_docs = []

    for doc in raw_documents:
        # Standard Agno chunking
        chunks = chunking_strategy.chunk(doc)
        for chunk in chunks:
            chunk_hash = get_content_hash(chunk.content)
            chunk.id = chunk_hash # Assign hash as ID for upsert logic
            final_chunked_docs.append(chunk)

    if final_chunked_docs:
        # Create a unique hash for the entire batch to satisfy LanceDB requirement
        batch_content_str = "".join([d.content for d in final_chunked_docs])
        batch_hash = get_content_hash(batch_content_str)
        
        # Explicitly pass content_hash to LanceDB upsert
        vector_db.upsert(
            documents=final_chunked_docs,
            content_hash=batch_hash
        )

        # Log specific metadata for this batch span
        opik.opik_context.update_current_span(
            metadata={
                "batch_index": i,
                "chunks_in_batch": len(final_chunked_docs)
            }
        )

# --- 6. Main Logic ---
@opik.track(name='Ingest NCERT')
def main():
    # 1. Verify Dataset
    if not os.path.exists(NCERT_PATH) or not os.listdir(NCERT_PATH):
        print("NCERT directory empty. Starting download...")
        download_dataset(base_path=NCERT_PATH, book_list=book_list)

    # 2. Load documents into memory
    print("Reading and formatting documents...")
    all_text_chunks = create_document(base_path=NCERT_PATH)
    total_docs = len(all_text_chunks)
    print(f"\nLoaded {total_docs} rows into memory.")

    if total_docs == 0:
        print("No documents found to process. Exiting.")
        return

    # 3. Initialize Vector DB table
    vector_db.create()

    # 4. Batch Processing Loop
    for i in tqdm(range(0, total_docs, BATCH_SIZE), desc="Processing Batches"):
        batch_texts = all_text_chunks[i : i + BATCH_SIZE]
        
        try:
            process_single_batch(i, batch_texts, vector_db, chunking_strategy)
        except Exception as e:
            print(f"\nError in batch starting at {i}: {e}")
            time.sleep(5) 

        time.sleep(SLEEP_TIME)

    print("\n\nSUCCESS! Knowledge Base populated safely.")
    
    # Force logs to send before closing
    opik.flush_tracker()

    
if __name__ == "__main__":
    main()



