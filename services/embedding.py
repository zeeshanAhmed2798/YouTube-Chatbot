from typing import List
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from config import settings

# Cache the embedder to avoid reloading
_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    return _embedder

def embed_chunks(chunks: List[Document], video_id: str):
    try:
        # Extract plain text from Documents 
        texts = [c.page_content.strip() for c in chunks if c.page_content and c.page_content.strip()]
        
        if not texts:
            raise ValueError("No valid text chunks found")
        
        # Make metadata 
        metas = [{"video_id": video_id, "chunk_id": i} for i, _ in enumerate(texts)]
        
        # Get embeddings
        embedder = get_embedder()
        vectors = embedder.embed_documents(texts)
        
        if len(vectors) != len(texts):
            raise ValueError(f"Embedding count mismatch: {len(vectors)} vs {len(texts)}")
        
        return texts, vectors, metas
    except Exception as e:
        print(f"Embedding error: {e}")
        raise
