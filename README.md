# 🎬 YouTube Chatbot

A powerful RAG-based chatbot that can answer questions about any YouTube video by analyzing its transcript.

## Features

- 📹 **YouTube Video Analysis**: Extract and process video transcripts
- 🌐 **Multi-language Support**: Automatically translates Hindi/Urdu to English
- 🤖 **AI-Powered Q&A**: Ask questions about video content
- 💾 **Vector Storage**: Uses Pinecone for efficient similarity search
- 🚀 **Fast Responses**: Powered by Groq's LLaMA model

## Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your API keys
4. Run: `streamlit run app.py`

## Deployment

This app is deployed on Streamlit Cloud and uses the following services:
- **Pinecone**: Vector database for embeddings
- **Groq**: LLM for generating responses
- **YouTube Transcript API**: For extracting video transcripts

## API Keys Required

- `PINECONE_API_KEY`: Your Pinecone API key
- `GROQ_API_KEY`: Your Groq API key

## Usage

1. Enter a YouTube video URL
2. Wait for transcript processing
3. Ask questions about the video content
4. Get AI-powered answers based on the transcript
