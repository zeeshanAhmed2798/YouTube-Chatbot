from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config import settings
from services.embedding import get_embedder
from services.vectorstore import get_or_create_index
import streamlit as st

# Cache these globally to avoid reinitializing
_embeddings = None
_vectorstore = None
_model = None

def get_embeddings():
    """Get cached embeddings"""
    global _embeddings
    if _embeddings is None:
        _embeddings = get_embedder()
    return _embeddings

def get_vectorstore():
    """Get cached vectorstore"""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = PineconeVectorStore.from_existing_index(
            index_name=settings.INDEX_NAME,
            embedding=get_embeddings(),
            namespace="",  # Use default namespace
            text_key="text",
        )
    return _vectorstore

def get_model():
    """Get cached model"""
    global _model
    if _model is None:
        _model = ChatGroq(
            model=settings.MODEL_NAME,
            api_key=settings.GROQ_API_KEY,
            temperature=0.1,
            max_tokens=900,
            top_p=0.9
        )
    return _model

def retrieve_context(query: str, k: int = 5):
    """Retrieve relevant context"""
    try:
        vectorstore = get_vectorstore()
        results = vectorstore.similarity_search(query, k=k)
        return results
    except Exception as e:
        return []

def make_prompt(query: str, context: str):
    """Create prompt"""
    template = ChatPromptTemplate.from_messages([
        ("system", 
         "You are a YT chatbot assistant. Use the provided context to answer accurately. "
         "CRITICAL INSTRUCTIONS:\n"
         "1. ALWAYS respond in Urdu only but write it in ENGLISH, If user give English Instructions then respond him in English otherwirse Always for all language respond in Urdu only but write it in ENGLISH\n"
         "2. Keep your response SHORT and CONCISE (maximum 10-12 sentences)\n"
         "3. Do NOT repeat the same information multiple times\n"
         "4. Focus on the main points only\n"
         "5. Do NOT generate repetitive content\n"
         "6. Even if the context is in Hindi/Urdu, respond in English\n"
         "7. Translate any Hindi/Urdu content to English in your response"),
        ("human", "Context:\n{context}\n\nQuestion:\n{query}")
    ])

    messages = template.format_messages(
        query=query,
        context=context
    )
    return messages

def answer(query: str):
    """Generate answer - Clean version"""
    try:
        # Retrieve context
        context_docs = retrieve_context(query, k=5)
        
        # Convert context_docs to string format
        if not context_docs:
            context_str = "No relevant context found in the video transcript."
        else:
            context_str = "\n\n".join([doc.page_content for doc in context_docs])
        
        # Create prompt
        prompt = make_prompt(query, context_str)
        
        # Get response
        model = get_model()
        response = model.invoke(prompt)
        
        # Limit response length to prevent repetition
        response_text = response.content
        
        # If response is too long, truncate it
        if len(response_text) > 500:
            truncated = response_text[:500]
            last_period = truncated.rfind('.')
            if last_period > 0:
                response_text = truncated[:last_period + 1]
            else:
                response_text = truncated + "..."
        
        return response_text
    except Exception as e:
        return f"Sorry, I encountered an error while processing your question: {str(e)}"