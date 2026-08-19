from fastapi.testclient import TestClient

from app.main import app
from app.rag_service import get_rag_engine


class FakeRagEngine:
    def ingest_text(self, file_name: str, content: str):
        return {
            "document_id": "doc_test",
            "chunks": 1,
            "file_name": file_name,
        }

    def chat(self, question: str, top_k: int):
        return {
            "answer": f"answered: {question}",
            "sources": [
                {
                    "document_id": "doc_test",
                    "file_name": "policy.md",
                    "chunk_index": 0,
                    "content": "报销需要主管审批。",
                    "score": 0.91,
                }
            ],
        }


def test_upload_text_document_indexes_content():
    app.dependency_overrides[get_rag_engine] = lambda: FakeRagEngine()
    client = TestClient(app)

    response = client.post(
        "/api/documents/upload",
        files={"file": ("policy.md", b"# Policy\nreimbursement needs approval", "text/markdown")},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {
        "document_id": "doc_test",
        "chunks": 1,
        "file_name": "policy.md",
    }


def test_chat_returns_answer_and_sources():
    app.dependency_overrides[get_rag_engine] = lambda: FakeRagEngine()
    client = TestClient(app)

    response = client.post("/api/chat", json={"question": "报销流程是什么？", "top_k": 3})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "answered: 报销流程是什么？"
    assert body["sources"][0]["file_name"] == "policy.md"
