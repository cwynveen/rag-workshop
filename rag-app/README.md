# RAG Example with LangChain, Ollama & Open Web UI

This repository demonstrates a Retrieval‑Augmented Generation (RAG) application powered by LangChain, Ollama, and the Open Web UI frontend.

---

## 🚀 Overview

- **`upstream-rag/`** – Upstream RAG service using standard Python base image  
- **`cg-rag/`** – Variant RAG service built on Chainguard Python image for tighter security  
- **`docker-compose.yml`** – Orchestrates two services:
  - `upstream-rag` or `cg-rag` (depending which you build) on port **8000**  
  - `open-webui` on port **3001**  
- **`resources/`** – Drop your PDFs (or other docs) here for ingestion  
- **`docker_best_practices.md`** – Notes on Dockerfile hardening  

---

## 📂 Folder Structure

```text
cg-rag/
├── docker-compose.yml
├── docker_best_practices.md
├── resources/
│   └── *.pdf            # Your knowledge documents
├── rag-app/
│   ├── Dockerfile       # Uses Chainguard Python base
│   ├── requirements.txt
│   └── main.py

upstream-rag/
├── docker-compose.yml
├── docker_best_practices.md
├── resources/
│   └── *.pdf            # Your knowledge documents
├── rag-app/
│   ├── Dockerfile       # Uses python:3.11-slim base
│   ├── requirements.txt
│   └── main.py

└── README.md
