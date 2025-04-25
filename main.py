from fastapi import FastAPI, UploadFile, File
from app.core.embedding_model import EmbeddingModel
from app.core.faiss_index import FaissIndex
from app.utils.chunker import split_text

import os

app = FastAPI()

# Load model and index once at startup
embedding_model = EmbeddingModel()
faiss_index = FaissIndex(dim=384)  # MiniLM has 384-dim embeddings

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")

    chunks = split_text(text)
    for chunk in chunks:
        emb = embedding_model.get_embedding(chunk)
        faiss_index.add(emb, chunk)

    return {"status": "success", "chunks": len(chunks)}
from fastapi import Request
from pydantic import BaseModel
from app.core.llm import generate_answer

class QueryRequest(BaseModel):
    question: str

@app.post("/query")
async def query_documents(query: QueryRequest):
    query_embedding = embedding_model.get_embedding(query.question)
    top_chunks = faiss_index.search(query_embedding)

    # Combine chunks into a prompt
    context = "\n".join(top_chunks)
    prompt = f"Answer the question based on the context below.\n\nContext:\n{context}\n\nQuestion: {query.question}"

    response = generate_answer(prompt)
    return {"answer": response}
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = content.decode("utf-8")

        chunks = split_text(text)
        for chunk in chunks:
            emb = embedding_model.get_embedding(chunk)
            faiss_index.add(emb, chunk)

        return {"status": "success", "chunks": len(chunks)}

    except Exception as e:
        print(f"🔥 Upload failed: {e}")
        return {"status": "error", "message": str(e)}
