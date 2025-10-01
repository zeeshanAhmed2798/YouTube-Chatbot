import time
from pinecone import Pinecone
from config import settings
from itertools import islice
from typing import Iterable
import streamlit as st

# Global variables to cache connections
_pc_client = None
_index = None

def get_pinecone_client():
    """Get or create Pinecone client (cached)"""
    global _pc_client
    if _pc_client is None:
        _pc_client = Pinecone(api_key=settings.PINECONE_API_KEY)
    return _pc_client

def batched(iterable: Iterable, n: int = 100):
    """Helper to batch data"""
    it = iter(iterable)
    while True:
        batch = list(islice(it, n))
        if not batch:
            break
        yield batch

def get_or_create_index(dim: int):
    """Get existing index or create new one"""
    global _index
    pc = get_pinecone_client()
    
    # Check if index exists
    existing = [i.name for i in pc.list_indexes()]
    
    if settings.INDEX_NAME in existing:
        # Index exists, just get it (reuse existing)
        _index = pc.Index(settings.INDEX_NAME)
        return _index
    else:
        # Create new index only if it doesn't exist
        pc.create_index(
            name=settings.INDEX_NAME,
            dimension=dim,
            metric="cosine",
            spec={
                "serverless": {
                    "cloud": settings.PINECONE_CLOUD,
                    "region": settings.PINECONE_REGION
                }
            }
        )
        
        # Wait for index to be ready
        while not pc.describe_index(settings.INDEX_NAME).status["ready"]:
            time.sleep(1)
        
        _index = pc.Index(settings.INDEX_NAME)
        return _index

def clear_vectors(index):
    """Clear all vectors from the index"""
    try:
        # Clear vectors from DEFAULT namespace (not kb)
        try:
            index.delete(delete_all=True, namespace="")  # Clear default namespace
        except Exception:
            pass  # No vectors to clear
        
        # Wait a moment for deletion to propagate
        time.sleep(2)
        
    except Exception as e:
        st.error(f"❌ Error clearing vectors: {e}")

def upsert_vectors(index, video_id: str, texts: list, vectors: list, metas: list):
    """Upsert vectors"""
    try:
        # Create payload
        payload = []
        for i, (vec, meta, txt) in enumerate(zip(vectors, metas, texts)):
            m = dict(meta)
            m["text"] = txt
            payload.append({"id": f"{video_id}::{i}", "values": vec, "metadata": m})
        
        # Batch upsert - NO NAMESPACE = DEFAULT
        total = 0
        for batch in batched(payload, 100):
            index.upsert(vectors=batch)  # No namespace = default namespace
            total += len(batch)
        
        st.success(f"✅ Video processed successfully! ({total} chunks stored)")
        
    except Exception as e:
        st.error(f"❌ Error processing video: {e}")
        raise

def get_vectorstore():
    """Get vectorstore for querying"""
    from services.embedding import get_embedder
    from langchain_pinecone import PineconeVectorStore
    
    embeddings = get_embedder()
    return PineconeVectorStore.from_existing_index(
        index_name=settings.INDEX_NAME,
        embedding=embeddings,
        namespace="",  # Use default namespace
        text_key="text",
    )