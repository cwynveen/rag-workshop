# RAG Example with LangChain, Ollama & Open Web UI

This repository demonstrates a Retrieval‑Augmented Generation (RAG) application powered by LangChain, Ollama, and the Open Web UI frontend. It is intended to showcase how using Chainguard as a base image for your AI applications can significantly reduce your security footprint (CVEs and hardened to DoD standards).

---

## 🚀 Overview
There are 2 main folders. 
- **`upstream-rag/`** – RAG service using standard Python base image from Docker Hub 
- **`cg-rag/`** – RAG service built on Chainguard Python image for tighter security
In each of these folders there are:  
- **`docker-compose.yml`** – Orchestrates two services:
  - `upstream-rag` or `cg-rag` (depending which you build) on port **8000**  
  - `open-webui` on port **3001**  
- **`resources/`** – Drop your PDFs (or other docs) here for ingestion. There are already 2 DoD container hardening pdfs in there
- **`docker_best_practices.md`** – This can be used to prioritize your specific container hardening requirements

---

## Setting up your Ubuntu server to run through the workshop
SSH into your Ubuntu server, we will need to install the following 
1. docker, docker-compose, ollama, grype, and syft
2. You will need to run the following commads to get ollama running and pull in the gemma3:4b model that we use
 
    ```shell
    export OLLAMA_HOST="0.0.0.0:11434"
    export OLLAMA_ORIGINS="*"
    ollama serve &
    ollama pull gemma3:4b
    ```

3. Clone the repo with the source code needed for the workshop:

    ```shell
    git clone https://github.com/cwynveen/rag-workshop.git
    ```

---

## Running through the workshop steps
1. Let start by moving into the upstream-rag folder and building our rag-app and running it with docker compose

    ```shell
    docker compose build --no-cache rag-app
    docker compose up -d
    ```

Open your browser at http://<EC2-PUBLIC-IP>:3001
Login (these can be dummy creds. admin@gmail.com)
Let's ask a question!
- What is Iron Bank?
Run grype against the image we just built

    ```shell
    grype <rag-app-upstream-rag>
    ```

Now let's spin everything down and test out building and running the same rag-app code on a Chainguard base image.

    ```shell
    docker compose down
    cd ..
    cd cg-rag
    docker compose build --no-cache rag-app
    docker compose up -d
    ```

Open your browser at http://<EC2-PUBLIC-IP>:3001
Login (these can be dummy creds. admin@gmail.com)
Let's ask a question!
- What is Iron Bank?
Run grype against the image we just built
    ```shell
    grype <cg-app-upstream-rag>
    ```
Much fewer CVE's from just a single line of code change in our Dockerfile FROM statement

---

## Let's inspect our Dockerfile for DoD Image Security best practices
Let's drop our Dockerfile in the Open Web UI to see where we are violating best practices:
.... needs improvement ...


