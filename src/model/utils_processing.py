from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
import os
import shutil
import time
import traceback
from dotenv import load_dotenv
import chromadb
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document

load_dotenv()  # Charge les variables d'environnement depuis un fichier .env

HF_TOKEN = os.getenv('API_TOKEN')
CHROMA_PATH = os.path.abspath(f"../{os.getenv('CHROMA_PATH')}")
BATCH_SIZE = int(os.getenv('BATCH_SIZE'))  # Ajustez cette valeur selon votre système
CHROMA_PATH = os.path.abspath(f"../{os.getenv('CHROMA_PATH')}")
BATCH_SIZE = int(os.getenv('BATCH_SIZE'))  # Ajustez cette valeur selon votre système
DATA_PATH_CSV = os.path.abspath(f"../{os.getenv('DATA_PATH_CSV')}")
COLLECTION_CSV = os.getenv('COLLECTION_CSV')
HF_TOKEN = os.getenv('API_TOKEN')

def load_documents(loader):
    try:
        documents = loader.load()
        if not documents:
            print("No documents were loaded.")
            return []

        print(f"Loaded {len(documents)} documents.")
        return documents
    except FileNotFoundError:
        print("Error: The file does not exist.")
    except Exception as e:
        print(f"An error occurred in load_documents: {e}")
        print(traceback.format_exc())
        return []

def split_text(documents: list[Document]):
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=100,
            length_function=len,
            add_start_index=True,
        )
        chunks = text_splitter.split_documents(documents)
        return chunks
    except Exception as e:
        print(f"An error occurred in split_text: {e}")

def chunk_documents(documents, batch_size):
    for i in range(0, len(documents), batch_size):
        yield documents[i:i + batch_size]

# Fonction pour supprimer une collection
def remove_collection(CHROMA_PATH, collection_name):
    try:
        collection_path = os.path.join(CHROMA_PATH, collection_name)
        if os.path.exists(collection_path):
            print(f"Removing existing collection: {collection_name}")
            shutil.rmtree(collection_path)
    except Exception as e:
        print(f"An error occurred while removing the collection: {e}")
        print(traceback.format_exc())

# Fonction pour sauvegarder des documents dans Chroma
def save_to_chroma(docs, CHROMA_PATH, collection_name, BATCH_SIZE, embedding_function):
    try:
        chroma_instance = Chroma.from_documents(docs, embedding_function, persist_directory=CHROMA_PATH, collection_name=collection_name)
        chroma_instance.persist()

        print("There are", chroma_instance._collection.count(), "documents in the collection")
    except Exception as e:
        print(f"An error occurred while saving to Chroma: {e}")
        print(traceback.format_exc())
