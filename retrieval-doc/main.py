from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List
import httpx
import io
import pdfplumber
import re
import traceback
from utils.vector_store import build_faiss_index, search_index
from utils.document_loader import download_and_parse_pdf
from pydantic import BaseModel




app = FastAPI()

class DocumentRequest(BaseModel):
    documents: HttpUrl

class ParsedResponse(BaseModel):
    chunks: List[str]
    
# Global FAISS index (simulate memory)
stored_chunks = []
faiss_index = None

@app.post("/api/v1/parse", response_model=ParsedResponse)
async def parse_document(request: DocumentRequest):
    print(f"Received request to parse document from URL: {request.documents}")

    try:
        async with httpx.AsyncClient() as client:
            print(f"Downloading PDF from: {request.documents}")
            response = await client.get(str(request.documents))

            response.raise_for_status()
            print("✅ Downloaded PDF successfully.")

        pdf_bytes = io.BytesIO(response.content)

        chunks = []
        current_chunk = ""

        with pdfplumber.open(pdf_bytes) as pdf:
            print(f"📄 PDF has {len(pdf.pages)} pages.")
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                lines = text.split("\n")
                for line in lines:
                    if re.match(r"^\d+(\.\d+)*\s", line):
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = line
                    else:
                        current_chunk += " " + line

        if current_chunk:
            chunks.append(current_chunk.strip())

        print(f"✅ Parsed {len(chunks)} chunks from PDF.")
        return ParsedResponse(chunks=chunks)

    except Exception as e:
        print("❌ ERROR during parsing:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class IndexRequest(BaseModel):
    url: HttpUrl

@app.post("/api/v1/index")
async def index_chunks(body: IndexRequest):
    global faiss_index, stored_chunks
    chunks = await download_and_parse_pdf(str(body.url))
    stored_chunks = chunks
    faiss_index, _ = build_faiss_index(chunks)
    return {"message": f"Indexed {len(chunks)} chunks."}

class QueryRequest(BaseModel):
    question: str

@app.post("/api/v1/search")
async def search_query(q: QueryRequest):
    if faiss_index is None:
        raise HTTPException(status_code=400, detail="Index not built.")
    results = search_index(faiss_index, q.question, stored_chunks)
    return {"answers": results}
# 🧪 Test the Flow
# Step 1 — Build index (FAISS):

# bash
# Copy
# Edit
# POST /api/v1/index
# Step 2 — Ask a question:

# bash
# Copy
# Edit
# POST /api/v1/search
# {
#   "question": "What is the grace period for premium payment?"
# }