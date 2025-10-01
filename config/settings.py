import os
from dotenv import load_dotenv

load_dotenv()

# Pinecone Configuration
PINECONE_API_KEY  = os.getenv("PINECONE_API_KEY")
INDEX_NAME        = os.getenv("PINECONE_INDEX_NAME", "yt-chatbot")  # FIXED: Add INDEX_NAME
PINECONE_CLOUD    = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION   = os.getenv("PINECONE_REGION", "us-east-1")
NAMESPACE         = os.getenv("NAMESPACE", "kb")

# Embeddings Configuration
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
CHUNK_SIZE           = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP        = int(os.getenv("CHUNK_OVERLAP", 200))

# LLM Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME   = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")

print(f"[settings] index={INDEX_NAME}, region={PINECONE_REGION}, model={EMBEDDING_MODEL_NAME}")