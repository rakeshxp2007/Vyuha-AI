import os
import pandas as pd
from datasets import load_dataset, load_from_disk


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
    documents=[]

    if not os.path.exists(base_path):
        print(f"Error: Path not found {base_path}")
        return []
    
    for filename in os.listdir(base_path):
        filename_str = str(filename)
        if filename_str.lower().endswith(".csv"):
            file_path = os.path.join(base_path, filename_str)
            try:
                ds = pd.read_csv(file_path).fillna("")
                # Convert to list of dictionaries
                records = ds.to_dict('records')
                subject = 'History' if 'history' in filename_str.lower() else 'geography'

                for row in records:
                    topic = str(row.get('Topic', 'N/A'))
                    question = str(row.get('Question', ''))
                    answer = str(row.get('Answer', ''))
                    explanation = str(row.get('Explanation', ''))

                    # Only create document if there is actual content
                    if question.strip() or explanation.strip():
                        doc = (
                            f"SOURCE: {filename_str}\n"
                            f"SUBJECT: {subject}\n"
                            f"TOPIC: {topic}\n"
                            f"QUESTION: {question}\n"
                            f"ANSWER: {answer}\n"
                            f"EXPLANATION: {explanation}"
                        )

                    documents.append(doc)
            except Exception as e:
                print(f"Skipping folder {filename_str} : {e}")
                
    return documents

if __name__ == "__main__":
    # Base directory for your POC
    base_path = "./NCERT"
    download_dataset(base_path=base_path, book_list=book_list)
    extracted_docs = create_document(base_path=base_path)
    print(f"Generate {len(extracted_docs)} documents")

