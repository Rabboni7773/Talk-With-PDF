<div align="center">

# 📄 Talk with PDF: Enterprise Edition
**A Production-Ready, Decoupled Retrieval-Augmented Generation (RAG) Microservices Architecture.**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FC6C05?style=for-the-badge)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Microservices](https://img.shields.io/badge/Architecture-Decoupled-8A2BE2?style=for-the-badge)

</div>

> **Talk with PDF** has been entirely re-architected for production environments. Moving away from tightly coupled components, this iteration completely decouples the FastAPI backend, the ChromaDB vector database, and the Redis state cache into independent, highly stable microservices. This design ensures maximum uptime, isolated fault tolerance, and independent scaling capabilities, while bypassing heavy declarative UI frameworks in favor of a lightweight, highly responsive JS/HTML frontend with asynchronous streaming.

---

## ✨ Production-Grade Features

* **🏗️ Decoupled Microservices:** The application logic, vector storage, and state management are isolated into dedicated containers. If one service spikes in load, the others remain fully stable.
* **🎨 Clean Web Interface:** A lightweight, highly responsive frontend built with standard HTML, CSS, and vanilla JavaScript (Streams API / SSE), rendered perfectly with Marked.js.
* **⚡ Real-Time Streaming:** Enjoy fluid, typewriter-style LLM responses streamed directly to the UI using asynchronous Python generators via Server-Sent Events.
* **🐳 Advanced Containerization:** Fully orchestrated using Docker Compose, establishing secure internal networks between the API, ChromaDB, and Redis.
* **🧠 Distributed Conversational Memory:** Maintains session-specific chat history via a standalone Redis node, replacing the older sliding-window array to allow the LLM to contextually track conversations across multiple stateless API requests.
* **🔍 High-Performance RAG Pipeline:** Ingests documents with LangChain (LCEL), maps semantics with HuggingFace embeddings (`BAAI/bge-small-en-v1.5`), and executes high-speed retrieval from the isolated Chroma container.

---

## 🛠️ Decoupled Technology Stack

| Service Layer | Technology | Role in Architecture |
| :--- | :--- | :--- |
| **Application API** | FastAPI, Uvicorn, Pydantic | Stateless API gateway and orchestration layer handling client requests, RAG pipelines, and LLM communication. |
| **Frontend Client** | HTML5 / CSS3 / Vanilla JS | Native web technologies serving a fast, responsive UI natively. |
| **LLM Engine** | ChatGroq | Utilizing `openai/gpt-oss-120b` for ultra-fast, low-latency inference. |
| **Embeddings** | HuggingFace | Utilizing `BAAI/bge-small-en-v1.5` for accurate semantic mapping. |
| **Vector Database** | ChromaDB | Isolated container strictly handling high-throughput vector embedding storage and nearest-neighbor retrieval. |
| **State Management** | Redis | Dedicated caching layer persisting ephemeral user session histories independent of the core API. |

---

## 📁 Architecture & Project Structure

```text
📦 talk-with-pdf
 ┣ 📂 templates/             # Frontend UI views
 │ ┣ 📜 index.html         # Document upload dropzone
 │ ┗ 📜 n_chat.html        # Main streaming chat interface
 ┣ 📂 utils/                 # Core logic
 │ ┗ 📜 rag_system.py      # Core LangChain pipeline & Chroma client
 ┣ 📜 .env                   # Environment variables (API keys)
 ┣ 📜 docker-compose.yaml    # Multi-container microservice orchestration
 ┣ 📜 Dockerfile             # Stateless API image build instructions
 ┣ 📜 main.py                # FastAPI entry point & routes
 ┗ 📜 requirements.txt       # Python dependencies
```

---

## 🚀 Backend API & Endpoints

The backend is driven by **FastAPI** (`main.py`), acting as a stateless gateway for serving templates, handling file operations, and managing the asynchronous streaming of LLM responses.

* `GET /`: Serves the initial file upload interface (`index.html`) via `Jinja2Templates`.
* `POST /upload`: Handles incoming `multipart/form-data`. Uploaded PDFs are securely written to the container's temporary storage.
* `GET /chat`: Triggers the document ingestion and vector database creation, then serves the chat interface (`n_chat.html`).
* `POST /chat/retrive`: The core interaction endpoint. Accepts a JSON payload validated via Pydantic (`ChatQuery`), routes the query through the LangChain pipeline, and returns an asynchronous `StreamingResponse` using Server-Sent Events (SSE).

---

## 🧠 The RAG Pipeline Data Flow

The retrieval logic is encapsulated within the `RAGSystem` class (`utils/rag_system.py`), designed around LangChain Expression Language (LCEL) for optimal data flow.

### 1. Ingestion & Embedding
* **Extraction:** `PyMuPDFLoader` parses the raw text from the uploaded PDF.
* **Chunking:** A `RecursiveCharacterTextSplitter` divides the text into overlapping semantic chunks (Chunk Size: `500`, Overlap: `50`).
* **Vectorization:** Embeddings are generated using the lightweight, highly efficient HuggingFace endpoint `BAAI/bge-small-en-v1.5`.
* **Isolated Storage:** Chunks are securely transmitted over the internal Docker network to be stored in the dedicated **ChromaDB** container under a unique session ID.

### 2. Distributed Retrieval & Generation
* **Parallel Execution:** A `RunnableParallel` chain executes the retrieval. It pulls the top 2 most semantically relevant chunks (`k=2`) from the Chroma service while independently retrieving the user's chat history from the **Redis** node.
* **Prompt Engineering:** The system prompt strictly anchors the LLM to the retrieved context, instructing it to gracefully reject out-of-scope queries and cite document sources when providing answers. The Groq LLM streams the formatted markdown response back through the API gateway.

---

## 💻 Frontend Implementation

The frontend utilizes clean, standard web technologies to communicate with the FastAPI backend via REST, avoiding the overhead of heavy SPA frameworks.

* **Upload Interface (`index.html`)**
    Features a drag-and-drop zone with instant visual feedback. It intercepts the file input, posts the data via `fetch()`, and upon receiving an `HTTP 200` success response, smoothly redirects the client to the chat workspace.
* **Streaming Chat UI (`n_chat.html`)**
    A modern, visually distinct chat interface. It leverages the browser's Streams API (`response.body.getReader()`) to intercept the SSE stream from FastAPI. Incoming text chunks are decoded dynamically and rendered in real-time using `marked.js` to ensure clean, accurate Markdown formatting (including code blocks and lists) as the LLM "types" out the response.

---

## 🚀 Deployment Guide

This decoupled architecture is designed for robust deployment on Linux environments.

### Prerequisites
* **Docker and Docker Compose** installed on your machine.
* API Keys for **Groq** and **HuggingFace**

### 1. Clone the Repository
```bash
git clone https://github.com/Rabboni7773/Talk-With-PDF.git
cd Talk-With-PDF
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory to store your API keys safely.
```bash
touch .env
```
Add the following to your `.env` file:
```ini
GROQ_API_KEY="your_groq_api_key_here"
HF_API="your_huggingface_api_key_here"
```
*(Note: Internal network variables connecting the API to the standalone `CHROMA_HOST` and `REDIS_URL` are strictly managed via Docker Compose for enhanced security, eliminating the need for hardcoded local paths.)*

### 3. Build and Launch the Microservices
Spin up the entire decoupled stack—initiating the FastAPI gateway, Redis cache node, and ChromaDB service independently:
```bash
docker-compose up --build -d
```

### 4. Access the UI
Open your web browser and navigate to:
* **Upload Interface:** `http://localhost:8080/`
* **Chat Interface:** `http://localhost:8080/chat` (You will be redirected here automatically after a successful upload).
</div>
