import streamlit as st
import os
from rag import build_faiss_index, answer_question

st.set_page_config(page_title="PDF RAG Chatbot", layout="wide")

st.title("📄 RAG Chatbot — Ask Questions from Your PDF")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

uploaded_pdf = st.file_uploader("Upload a PDF", type=["pdf"])

# ✅ Check file size (10 MB limit)
MAX_FILE_SIZE_MB = 10

if uploaded_pdf:
    if uploaded_pdf.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"PDF must be smaller than {MAX_FILE_SIZE_MB} MB")
        st.stop()

    # Save file
    with open("uploaded.pdf", "wb") as f:
        f.write(uploaded_pdf.getbuffer())

    # Reset chat history & build index
    st.session_state.chat_history = []
    build_faiss_index("uploaded.pdf")
    st.success("PDF uploaded and indexed successfully.")

# Chat Input
query = st.text_input("Ask a question about the PDF")

if st.button("Ask") and query:
    answer = answer_question(query)
    st.session_state.chat_history.append(("You", query))
    st.session_state.chat_history.append(("Bot", answer))

# Display chat history
for role, msg in st.session_state.chat_history:
    if role == "You":
        st.markdown(f"**🧍 You:** {msg}")
    else:
        st.markdown(f"**🤖 Bot:** {msg}")
# app.py (add below your existing code)
st.markdown("---")
st.header("📊 PDF-to-Excel Agent")

uploaded_pdfs = st.file_uploader(
    "Upload multiple PDFs for Excel processing", 
    type=["pdf"], 
    accept_multiple_files=True
)

questions = st.text_area(
    "Enter questions to extract (one per line)", 
    value="Title of document?\nKey dates?\nMentioned products?"
).splitlines()

if st.button("Process PDFs to Excel") and uploaded_pdfs:
    pdf_paths = []
    for uploaded_file in uploaded_pdfs:
        path = uploaded_file.name
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        pdf_paths.append(path)

    from rag import process_pdfs_to_excel
    df = process_pdfs_to_excel(pdf_paths, questions)
    st.success("✅ Excel file generated!")
    st.dataframe(df)
