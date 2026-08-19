from fastapi import Depends, FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .rag_service import RagEngine, extract_text, get_rag_engine


app = FastAPI(title="RAG Service", version="0.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    engine: RagEngine = Depends(get_rag_engine),
):
    raw = await file.read()
    content = extract_text(file.filename or "uploaded.txt", raw)
    return engine.ingest_text(file.filename or "uploaded.txt", content)


@app.post("/api/chat")
def chat(request: ChatRequest, engine: RagEngine = Depends(get_rag_engine)):
    return engine.chat(request.question, request.top_k)
