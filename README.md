# rag-java-langchain-rag-service

FastAPI + LangChain + Chroma + Ollama RAG 服务项目，负责文档解析、文本切分、向量化入库、相似检索和本地大模型问答。

## 项目关系

```text
rag-java-langchain-frontend
  -> rag-java-langchain-backend
  -> rag-java-langchain-rag-service
  -> Ollama
```

默认端口：

```text
RAG 服务:  http://localhost:8001
Ollama:    http://localhost:11434
Java 后端: http://localhost:8080
前端页面:  http://localhost:5173
```

## 准备本地模型

安装并启动 Ollama 后，拉取聊天模型和 Embedding 模型：

```bash
ollama pull qwen2.5:7b
ollama pull bge-m3
```

默认模型配置：

```text
聊天模型: qwen2.5:7b
向量模型: bge-m3
Ollama:   http://localhost:11434
```

如需修改：

```bash
export OLLAMA_MODEL=qwen2.5:7b
export EMBEDDING_MODEL=bge-m3
export OLLAMA_BASE_URL=http://localhost:11434
```

## 安装依赖

```bash
cd /Users/lijunwei/PycharmProjects/rag-java-langchain-rag-service
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## 本地启动

```bash
cd /Users/lijunwei/PycharmProjects/rag-java-langchain-rag-service
. .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

访问地址：

```text
http://localhost:8001
```

健康检查：

```bash
curl http://localhost:8001/api/health
```

期望返回：

```json
{"status":"ok"}
```

## API

上传文档：

```text
POST /api/documents/upload
Content-Type: multipart/form-data
file: 上传文件
```

示例：

```bash
curl -F "file=@README.md" http://localhost:8001/api/documents/upload
```

响应示例：

```json
{
  "document_id": "文档ID",
  "file_name": "README.md",
  "chunks": 3
}
```

问答：

```text
POST /api/chat
Content-Type: application/json
```

示例：

```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"这个项目有哪些模块？","top_k":5}'
```

响应示例：

```json
{
  "answer": "回答内容",
  "sources": [
    {
      "document_id": "文档ID",
      "file_name": "README.md",
      "chunk_index": 0,
      "content": "引用片段",
      "score": 0.88
    }
  ]
}
```

## 数据目录

Chroma 向量库默认持久化到：

```text
data/chroma/
```

该目录属于本地运行数据，不提交到 Git。

## 测试

```bash
cd /Users/lijunwei/PycharmProjects/rag-java-langchain-rag-service
. .venv/bin/activate
pytest -q
```

## 启动顺序

1. 启动 Ollama，并确认 `qwen2.5:7b`、`bge-m3` 已拉取
2. 启动当前 RAG 服务
3. 启动 `rag-java-langchain-backend`
4. 启动 `rag-java-langchain-frontend`
