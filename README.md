# rag-java-langchain-rag-service

FastAPI + LangChain + Chroma + Ollama RAG 服务项目，负责文档解析、切分、向量化入库、检索和大模型问答。

## 准备本地模型

安装并启动 Ollama 后拉取模型：

```bash
ollama pull qwen2.5:7b
ollama pull bge-m3
```

可选环境变量：

```bash
export OLLAMA_MODEL=qwen2.5:7b
export EMBEDDING_MODEL=bge-m3
export OLLAMA_BASE_URL=http://localhost:11434
```

## 启动

```bash
cd /Users/lijunwei/PycharmProjects/rag-java-langchain-rag-service
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

健康检查：

```bash
curl http://localhost:8001/api/health
```

## API

```text
POST /api/documents/upload
POST /api/chat
GET  /api/health
```
