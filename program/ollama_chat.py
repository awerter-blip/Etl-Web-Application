from pathlib import Path

import chromadb
import ollama
#from pypdf import PdfReader


# Beállítások
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "local_documents"

#CHAT_MODEL = "llama3.2:1b"
CHAT_MODEL = "qwen3.5:2b"
EMBED_MODEL = "nomic-embed-text"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
TOP_K = 4

def response(prompt, messages):
    
    
    response = ollama.chat(
            model=CHAT_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

    print("\nVÁLASZ:")
    print(response["message"]["content"])
    return response["message"]["content"]