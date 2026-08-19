import hashlib
import io
import os
from functools import lru_cache
from typing import Any, Dict, List

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader


def extract_text(file_name: str, raw: bytes) -> str:
    if file_name.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(raw))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return raw.decode("utf-8", errors="ignore")


class RagEngine:
    def __init__(self):
        self.persist_directory = os.getenv("CHROMA_DIR", "data/chroma")
        self.collection_name = os.getenv("CHROMA_COLLECTION", "local_knowledge")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "bge-m3")
        self.chat_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.embeddings = OllamaEmbeddings(
            model=self.embedding_model,
            base_url=self.ollama_base_url,
        )
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory,
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=int(os.getenv("CHUNK_SIZE", "800")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "120")),
            separators=["\n\n", "\n", "。", "！", "？", ".", " ", ""],
        )
        self.llm = ChatOllama(
            model=self.chat_model,
            base_url=self.ollama_base_url,
            temperature=0.1,
        )

    def ingest_text(self, file_name: str, content: str) -> Dict[str, Any]:
        normalized = content.strip()
        if not normalized:
            return {"document_id": "", "file_name": file_name, "chunks": 0}

        document_id = hashlib.sha256((file_name + normalized).encode("utf-8")).hexdigest()[:16]
        chunks = self.splitter.split_text(normalized)
        documents = [
            Document(
                page_content=chunk,
                metadata={
                    "document_id": document_id,
                    "file_name": file_name,
                    "chunk_index": index,
                },
            )
            for index, chunk in enumerate(chunks)
        ]
        ids = [f"{document_id}_{index}" for index in range(len(documents))]
        self.vectorstore.add_documents(documents, ids=ids)
        return {"document_id": document_id, "file_name": file_name, "chunks": len(documents)}

    def chat(self, question: str, top_k: int) -> Dict[str, Any]:
        docs_with_scores = self.vectorstore.similarity_search_with_score(question, k=top_k)
        sources = [
            {
                "document_id": doc.metadata.get("document_id", ""),
                "file_name": doc.metadata.get("file_name", ""),
                "chunk_index": int(doc.metadata.get("chunk_index", 0)),
                "content": doc.page_content,
                "score": float(score),
            }
            for doc, score in docs_with_scores
        ]
        context = "\n\n".join(
            f"[来源{i + 1}: {source['file_name']}#{source['chunk_index']}]\n{source['content']}"
            for i, source in enumerate(sources)
        )
        prompt = (
            "你是一个企业知识库问答助手。请只根据给定资料回答用户问题。"
            "如果资料中没有答案，请回答“资料中未提及”。\n\n"
            f"资料:\n{context or '无'}\n\n"
            f"用户问题:\n{question}\n\n"
            "请给出简洁准确的中文回答。"
        )
        answer = self.llm.invoke(prompt).content
        return {"answer": answer, "sources": sources}


@lru_cache
def get_rag_engine() -> RagEngine:
    return RagEngine()
