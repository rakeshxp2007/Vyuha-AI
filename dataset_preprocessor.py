import os
import pandas as pd
from datasets import load_dataset


book_list=['KadamParth/NCERT_History_11th',
           'KadamParth/NCERT_History_12th',
           'KadamParth/NCERT_Geography_11th',
           'KadamParth/NCERT_Geography_12th']




# Download Files from HuggingFace Dataset Dierectory
def download_dataset(base_path, book_list):
    os.makedirs(base_path,exist_ok=True)

    for books in book_list:        
        folder = books.split('/')[-1]
        save_path = os.path.join(base_path,f"{folder}.csv")
        if not os.path.exists(save_path):
            print(f"Downloading and processing: {books}...")

            try:
                loaded_data = load_dataset(books, split='train')    
                loaded_data.to_csv(save_path, index=False)
                print(f'Successfuly save to: {save_path}')
            except Exception as e:
                print(f" Failed to download {books}: {e}")
        else:
            print(f"File already exists: {save_path}")

# Create document

def create_document(base_path):
    processed_docs = [] 

    if not os.path.exists(base_path):
        print(f"Error: Path not found {base_path}")
        return []
    
    for filename in os.listdir(base_path):
        filename_str = str(filename)
        if filename_str.lower().endswith(".csv"):
            file_path = os.path.join(base_path, filename_str)
            try:
                ds = pd.read_csv(file_path).fillna("")
                records = ds.to_dict('records')
                
                # Extract clean subject/book name
                # e.g., "NCERT_History_11th.csv" -> "History_11th"
                clean_source = filename_str.replace('.csv', '')
                subject = 'History' if 'history' in filename_str.lower() else 'Geography'

                for row in records:
                    topic = str(row.get('Topic', 'General'))
                    question = str(row.get('Question', ''))
                    answer = str(row.get('Answer', ''))
                    explanation = str(row.get('Explanation', ''))

                    # Skip empty rows
                    if not question.strip() and not explanation.strip():
                        continue

                    # 1. THE RICH TEXT (For Embedding & LLM Reading)
                    # We keep the "Context Injection" here because it helps vector search
                    text_content = (
                        f"SUBJECT: {subject} | TOPIC: {topic}\n"
                        f"Q: {question}\n"
                        f"A: {answer}\n"
                        f"EXP: {explanation}"
                    )

                    # 2. THE STRUCTURED METADATA (For Opik & Database Filtering)
                    meta = {
                        "source": clean_source,
                        "subject": subject,
                        "topic": topic,
                        "type": "Q&A"
                    }

                    # Return both as a dictionary
                    processed_docs.append({
                        "content": text_content,
                        "metadata": meta
                    })
                    
            except Exception as e:
                print(f"Skipping file {filename_str} : {e}")
                
    return processed_docs

if __name__ == "__main__":
    # Base directory for POC
    base_path = "./NCERT"
    download_dataset(base_path=base_path, book_list=book_list)
    
    # Run the function that builds the dictionaries
    extracted_docs = create_document(base_path=base_path)
    print(f"\nGenerated {len(extracted_docs)} documents.")
    
    # --- VERIFICATION STEP ---
    # Print the very first document to see how it is structured
    if extracted_docs:
        print("\n--- SAMPLE DOCUMENT (Row 1) ---")
        print("1. THE CONTENT (What the LLM reads):")
        print(extracted_docs[0]['content'])
        
        print("\n2. THE METADATA (What LanceDB uses for filtering/tracking):")
        print(extracted_docs[0]['metadata'])
        print("-------------------------------\n")

