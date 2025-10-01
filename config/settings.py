import os
import streamlit as st
from dotenv import load_dotenv

# Load .env file for local development
load_dotenv()

def get_secret(key: str, default: str = None):
    """Get secret from Streamlit secrets or environment variable"""
    try:
        # Try Streamlit secrets first (for cloud deployment)
        return st.secrets[key]
    except:
        # Fallback to environment variable (for local development)
        return os.getenv(key, default)

# Pinecone Configuration
PINECONE_API_KEY = get_secret("PINECONE_API_KEY")
INDEX_NAME = get_secret("PINECONE_INDEX_NAME", "yt-chatbot")
PINECONE_CLOUD = get_secret("PINECONE_CLOUD", "aws")
PINECONE_REGION = get_secret("PINECONE_REGION", "us-east-1")
NAMESPACE = get_secret("NAMESPACE", "kb")

# Embeddings Configuration
EMBEDDING_MODEL_NAME = get_secret("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
CHUNK_SIZE = int(get_secret("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(get_secret("CHUNK_OVERLAP", "200"))

# LLM Configuration
GROQ_API_KEY = get_secret("GROQ_API_KEY")
MODEL_NAME = get_secret("MODEL_NAME", "llama-3.1-8b-instant")

print(f"[settings] index={INDEX_NAME}, region={PINECONE_REGION}, model={EMBEDDING_MODEL_NAME}")