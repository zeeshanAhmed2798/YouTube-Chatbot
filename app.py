import streamlit as st
import time
from utils.text import extract_video_id
from services.yt_loader import get_transcript
from services.chunking import make_chunks
from services.embedding import get_embedder, embed_chunks
from services.vectorstore import get_or_create_index, clear_vectors, upsert_vectors
from services.qa import answer
from config import settings

# Configure page
st.set_page_config(
    page_title="YouTube Chatbot", 
    page_icon="🎬",
    layout="centered"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "video_processed" not in st.session_state:
    st.session_state.video_processed = False
if "current_video_id" not in st.session_state:
    st.session_state.current_video_id = None

# Simple header
st.title("🎬 YouTube Chatbot")
st.caption("Ask questions about any YouTube video")

# Video input section
with st.container():
    st.subheader("📹 Add Video")
    video_url = st.text_input(
        "YouTube URL", 
        placeholder="https://www.youtube.com/watch?v=...",
        help="Paste any YouTube video URL here"
    )
    
    if video_url:
        video_id = extract_video_id(video_url)
        st.success(f"Video ID: {video_id}")

# Process video
if video_url and not st.session_state.video_processed:
    video_id = extract_video_id(video_url)
    
    with st.spinner("Processing video..."):
        # Get transcript
        transcript = get_transcript(video_id)
        
        # Fixed condition - check for actual error messages, not just "not"
        if transcript and not any(error in transcript.lower() for error in ["error", "disabled", "not found", "no transcript"]):
            st.success("✅ Transcript found!")
            
            # Show progress
            with st.spinner("Processing video..."):
                # Create chunks
                chunks = make_chunks(transcript)
                
                # Create embeddings (FIXED: correct function call)
                texts, vectors, metas = embed_chunks(chunks, video_id)
                
                # Store in Pinecone
                index = get_or_create_index(dim=384)
                clear_vectors(index)
                upsert_vectors(index, video_id, texts, vectors, metas)
                
                # Update session state
                st.session_state.video_processed = True
                st.session_state.current_video_id = video_id
                st.session_state.messages = []
                
                st.success("🎉 Video ready for questions!")
        else:
            st.error("❌ No transcript available for this video.")

# Chat interface
if st.session_state.video_processed:
    st.subheader("💬 Chat")
    
    # Show current video info
    st.info(f"📺 Currently analyzing: {st.session_state.current_video_id}")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about the video..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = answer(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Simple controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Video"):
            # Clear session state
            st.session_state.video_processed = False
            st.session_state.current_video_id = None
            st.session_state.messages = []
            
            # Clear vectors from database - CLEAR DEFAULT NAMESPACE
            try:
                index = get_or_create_index(dim=384)  # Use standard dimension
                clear_vectors(index)  # This will now clear default namespace
                st.success("✅ Database cleared! Ready for new video.")
            except Exception as e:
                st.error(f"❌ Error clearing database: {e}")
            
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
