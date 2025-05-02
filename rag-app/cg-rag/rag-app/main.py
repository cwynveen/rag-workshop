import os, glob, time, logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# LangChain imports
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_ollama.llms import OllamaLLM
from langchain.chains import ConversationalRetrievalChain

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="RAG → Ollama Conversational")

# — Configuration —
PERSIST_DIR = "vectordb"
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemma3:4b")
OLLAMA_URL = os.getenv("OLLAMA_SERVER_URL", "http://host.docker.internal:11434")

# — Ingest & persist documents —
os.makedirs(PERSIST_DIR, exist_ok=True)
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
vectordb = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)

if vectordb._collection.count() == 0:
    logging.info("Index empty; ingesting…")
    docs = TextLoader("../docker_best_practices.md").load()
    for pdf in sorted(glob.glob("/resources/*.[pP][dD][fF]")):
        docs += PyPDFLoader(pdf).load()
    vectordb.add_documents(docs)
    vectordb.persist()
    logging.info("Stored %d chunks", vectordb._collection.count())

# — Build the LLM —
llm = OllamaLLM(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0.0)

# — Conversational RAG chain —
conv_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectordb.as_retriever(search_kwargs={"k": 3}),
    system_prompt=(
        "You are a helpful assistant. Use the context to answer factual questions, "
        "but you can also chat conversationally."
    ),
)

# — OpenAI-compatible shim for Open Web UI —
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


def make_chat_response(model: str, answer: str) -> ChatCompletionResponse:
    return ChatCompletionResponse(
        id=f"chatcmpl-{int(time.time())}",
        created=int(time.time()),
        model=model,
        choices=[Choice(
            index=0,
            message=ChatMessage(role="assistant", content=answer),
            finish_reason="stop",
        )],
        usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    )

@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [{"id": DEFAULT_MODEL, "object": "model", "owned_by": "ollama"}],
    }

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def openai_chat(req: ChatCompletionRequest):
    user_msg = req.messages[-1].content
    result = conv_chain({"question": user_msg})
    return make_chat_response(req.model, result["answer"])
