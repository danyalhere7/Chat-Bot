# rag.py

import os
from pathlib import Path
import pandas as pd
import json
import re
from dotenv import load_dotenv
from utils import extract_text_from_pdf, chunk_text

# Optional OCR support
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from langchain_openai import ChatOpenAI

load_dotenv()

# ------------------------------
# OCR Helper
# ------------------------------
def extract_text_with_ocr(pdf_path):
    """Fallback OCR extraction if normal PDF text extraction fails"""
    if not OCR_AVAILABLE:
        print("❌ OCR libraries not installed. Install pdf2image and pytesseract for OCR support.")
        return ""
    text = ""
    pages = convert_from_path(pdf_path)
    for page in pages:
        text += pytesseract.image_to_string(page) + "\n"
    return text

# ------------------------------
# Safe JSON parsing
# ------------------------------
def safe_parse_json(text):
    """Try to parse JSON, fallback to regex, otherwise return raw text"""
    try:
        return json.loads(text)
    except:
        # Try to extract JSON-like structure from text
        match = re.search(r"{.*}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                return {"raw_text": text[:500]}
        else:
            return {"raw_text": text[:500]}

# ------------------------------
# LLM Extraction
# ------------------------------
def extract_all_fields_from_text(text):
    """
    Use LLM to extract all possible fields from text in JSON format.
    Returns a dictionary.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = f"""
You are a data extraction assistant.
Extract all information from the following document and return ONLY a valid JSON object.
All keys should be strings, all values should be strings or null.
Do NOT write any text outside JSON. Do NOT explain anything.
If a field is missing, leave it as null.

Document:
{text}

Return JSON ONLY:
"""
    response = llm.invoke(prompt)
    data = safe_parse_json(response.content)
    return data

# ------------------------------
# Auto PDF Processing Agent
# ------------------------------
def auto_process_pdfs(pdf_folder, output_file="pdf_data.xlsx", use_ocr=True):
    """
    Automatically process all PDFs in a folder, extract all fields, and save to Excel.
    Handles long PDFs by chunking text.
    """
    pdf_files = [
        os.path.join(pdf_folder, f)
        for f in os.listdir(pdf_folder)
        if f.lower().endswith(".pdf")
    ]
    if not pdf_files:
        print(f"❌ No PDFs found in folder: {pdf_folder}")
        return

    all_data = []

    for pdf_path in pdf_files:
        print(f"\nProcessing {pdf_path} ...")
        # Step 1: Extract text
        text = extract_text_from_pdf(pdf_path)
        if not text.strip() and use_ocr:
            print(f"⚠️ No text found or PDF corrupted, using OCR for {pdf_path}")
            text = extract_text_with_ocr(pdf_path)

        if not text.strip():
            print(f"❌ Skipping {pdf_path}, no readable text available.\n")
            continue

        # Step 2: Chunk text if large
        chunks = chunk_text(text)
        merged_data = {}

        for c in chunks:
            data_chunk = extract_all_fields_from_text(c)
            # Merge chunk data, prioritize non-null values
            for k, v in data_chunk.items():
                if k not in merged_data or not merged_data[k]:
                    merged_data[k] = v

        merged_data["File Name"] = Path(pdf_path).name
        all_data.append(merged_data)

    if all_data:
        # Flatten nested JSON for Excel
        df = pd.json_normalize(all_data)
        # Save Excel safely
        if os.path.exists(output_file):
            os.remove(output_file)
        df.to_excel(output_file, index=False)
        print(f"\n✅ All PDFs processed. Data saved to {output_file}")
        return df
    else:
        print("⚠️ No data to save. All PDFs were empty or unreadable.")
        return None

# ------------------------------
# Example Usage
# ------------------------------
if __name__ == "__main__":
    folder = "pdfs"  # folder containing your PDFs
    auto_process_pdfs(folder)
