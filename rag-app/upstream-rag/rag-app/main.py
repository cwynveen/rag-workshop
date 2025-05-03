# rag‑app/main.py
import os
import glob
import time
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader, PyPDFLoader

from langchain.chains import RetrievalQA, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_ollama.llms import OllamaLLM

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="RAG → Ollama")

# — Config —
PERSIST_DIR   = "vectordb"
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemma3:4b")
OLLAMA_URL    = os.getenv("OLLAMA_SERVER_URL", "http://host.docker.internal:11434")

# — Ingest & persist your docs —
os.makedirs(PERSIST_DIR, exist_ok=True)
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
vectordb   = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)

if vectordb._collection.count() == 0:
    logging.info("Index empty; ingesting…")
    # load your markdown guide mounted at container root
    docs = TextLoader("/docker_best_practices.md").load()
    # load any PDFs you put under ./resources on your Mac
    for pdf in sorted(glob.glob("/resources/*.pdf")):
        docs += PyPDFLoader(pdf).load()
    vectordb.add_documents(docs)
    vectordb.persist()
    logging.info("Stored %d chunks", vectordb._collection.count())

# — Build the LLM, retriever & RAG chain —
llm       = OllamaLLM(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0.0)
retriever = vectordb.as_retriever(search_kwargs={"k": 3})
qa_chain  = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
)

# — Build a free‑form fallback chain with its own system prompt —
fallback_system   = "You are a helpful assistant. Provide an informative answer to the user's question."
sys_msg_fb        = SystemMessagePromptTemplate.from_template(fallback_system)
human_msg_fb      = HumanMessagePromptTemplate.from_template("{question}")
fallback_prompt   = ChatPromptTemplate.from_messages([sys_msg_fb, human_msg_fb])
fallback_chain    = LLMChain(llm=llm, prompt=fallback_prompt)

# — OpenAI‑compatible shim for Open Web UI —
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage]

class Choice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[Choice]
    usage: dict = {}

@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [{"id": DEFAULT_MODEL, "object": "model", "owned_by": "ollama"}],
    }

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def openai_chat(req: ChatCompletionRequest):
    last = req.messages[-1]
    if last.role != "user":
        raise HTTPException(400, "Last message must be role=user")

    user_q = last.content

    # 1) Retrieve relevant docs
    docs = retriever.get_relevant_documents(user_q)
    logging.info(f"🔍 Retrieved {len(docs)} docs for query: {user_q!r}")

    # 2) Try RAG chain first
    if docs:
        rag_ans = qa_chain.run(user_q).strip()
        logging.info(f"📄 RAG answer: {rag_ans!r}")
        if rag_ans.lower().startswith("i don't know"):
            logging.info("⚡ RAG said 'I don't know' → using fallback LLM")
            out = fallback_chain.invoke({"question": user_q})
            answer = out.get("text") if isinstance(out, dict) else str(out)
        else:
            answer = rag_ans
    else:
        # 3) No docs → fallback directly
        logging.info("⚡ No docs found → using fallback LLM")
        out = fallback_chain.invoke({"question": user_q})
        answer = out.get("text") if isinstance(out, dict) else str(out)

    return ChatCompletionResponse(
        id=f"chatcmpl-{int(time.time())}",
        created=int(time.time()),
        model=req.model,
        choices=[Choice(
            index=0,
            message=ChatMessage(role="assistant", content=answer),
            finish_reason="stop"
        )],
        usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    )
