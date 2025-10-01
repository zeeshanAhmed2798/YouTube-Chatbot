import os
import streamlit as st
from dotenv import load_dotenv

# Load .env file for local development
load_dotenv()

# Try to get from Streamlit secrets first, then .env
def get_secret(key: str, default: str = None):
    try:
        return st.secrets[key]
    except:
        return os.getenv(key, default)

# Pinecone settings
PINECONE_API_KEY = get_secret("PINECONE_API_KEY")
PINECONE_INDEX_NAME = get_secret("PINECONE_INDEX_NAME", "yt-chatbot")
PINECONE_CLOUD = get_secret("PINECONE_CLOUD", "aws")
PINECONE_REGION = get_secret("PINECONE_REGION", "us-east-1")

# Embedding settings
EMBEDDING_MODEL_NAME = get_secret("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
CHUNK_SIZE = int(get_secret("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(get_secret("CHUNK_OVERLAP", "200"))
NAMESPACE = get_secret("NAMESPACE", "")

# LLM settings
GROQ_API_KEY = get_secret("GROQ_API_KEY")
MODEL_NAME = get_secret("MODEL_NAME", "llama-3.1-8b-instant")

print(f"[settings] index={PINECONE_INDEX_NAME}, region={PINECONE_REGION}, model={EMBEDDING_MODEL_NAME}")