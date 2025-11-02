from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import settings

def make_chunks(transcript: str):
    """Create chunks from transcript - same as notebook"""
    doc = Document(page_content=transcript)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    return splitter.split_documents([doc])
