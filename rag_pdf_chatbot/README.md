# PDF RAG Chatbot MVP

## Overview
A RAG chatbot that answers questions **only from uploaded PDFs** using OpenAI embeddings and GPT.

## Features
- Upload **one PDF at a time** (max 10 MB)  
- Previous document & embeddings deleted on new upload  
- Chat history resets per PDF  
- RAG pipeline: PDF → Text → Chunking → FAISS → GPT  
- Simple Streamlit UI  

## Requirements
- Python 3.10+  
- Packages: `streamlit`, `langchain`, `langchain-openai`, `langchain-community`, `faiss-cpu`, `pypdf`, `python-dotenv`

## Setup
1. Clone repo  
2. Add `.env` file with your OpenAI key  
3. Install dependencies: `pip install -r requirements.txt`  
4. Run: `streamlit run app.py`  

## Usage
1. Open app in browser  
2. Upload PDF (max 10 MB)  
3. Ask questions  
4. Chat resets when a new PDF is uploaded  

## Notes
- FAISS index uses pickle — safe for your local PDFs  
- OpenAI key must be valid  
