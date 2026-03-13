from typing import List, Tuple
import chromadb
from langchain_ollama import OllamaEmbeddings, ChatOllama

from src.utils.config_loader import load_config


config = load_config()

VECTOR_DB_PATH = config["paths"]["vector_db"]
COLLECTION_NAME = config["vector_database"]["collection_name"]

EMBED_MODEL = config["models"]["embedding_model"]
LLM_MODEL = config["models"]["llm_model"]

TOP_K = config["retrieval"]["top_k"]


def get_collection():
    """
    Inicializa conexión con ChromaDB
    """
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    return client.get_collection(COLLECTION_NAME)


def get_embedder():
    """
    Inicializa modelo de embeddings
    """
    return OllamaEmbeddings(model=EMBED_MODEL)


def retrieve_context(question: str) -> Tuple[str, List[str]]:
    """
    Recupera contexto relevante desde la base vectorial
    """

    embedder = get_embedder()
    collection = get_collection()

    query_vector = embedder.embed_query(question)

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=TOP_K,
        include=["documents", "metadatas", "distances"]
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    blocks = []
    sources = []

    for i, doc in enumerate(documents):

        meta = metadatas[i] if i < len(metadatas) else {}
        dist = distances[i] if i < len(distances) else None

        source = meta.get("source", "unknown")
        chunk = meta.get("chunk", "N/A")

        blocks.append(
            f"[Fuente: {source} | Chunk: {chunk} | Score: {dist}]\n{doc}"
        )

        sources.append(
            f"{source} (chunk {chunk})"
        )

    context = "\n\n---\n\n".join(blocks)

    return context, sources


def build_prompt(question: str, context: str) -> str:
    """
    Construye prompt médico para el LLM
    """

    return f"""
Eres un asistente médico especializado en pediatría.

Usa únicamente el contexto proporcionado para responder.

Reglas:
- No inventes información.
- Si la respuesta no está en el contexto, responde:
  "No encontré esa información en la base médica."
- Explica de forma clara para estudiantes de medicina o médicos.

Contexto:
{context}

Pregunta:
{question}

Respuesta:
""".strip()


def ask(question: str) -> str:
    """
    Ejecuta pipeline completo de RAG
    """

    context, sources = retrieve_context(question)

    llm = ChatOllama(model=LLM_MODEL)

    prompt = build_prompt(question, context)

    response = llm.invoke(prompt)

    print("\n=== FUENTES ===")
    for s in sources:
        print(f"- {s}")

    print("\n=== RESPUESTA ===")
    print(response.content)

    return response.content


def interactive():
    """
    CLI interactiva para probar el RAG
    """

    print("\nAsistente RAG de Pediatría (escribe 'salir' para terminar)\n")

    while True:

        question = input("Pregunta: ").strip()

        if not question:
            continue

        if question.lower() in {"salir", "exit", "quit"}:
            break

        try:
            ask(question)

        except Exception as e:
            print(f"\n[ERROR] {e}\n")