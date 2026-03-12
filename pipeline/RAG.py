import re
import chromadb
from langchain_ollama import OllamaEmbeddings, ChatOllama
import json
data = {}

try:
    with open("var.json", "r", encoding="utf-8") as file:
        data = json.load(file)
   
except FileNotFoundError:
    print("Archivo var.json no existe, se usarán valores por defecto")

DB_PATH = data.get("DB_PATH", "data/chroma_db")
COLLECTION_NAME = data.get("COLLECTION_NAME", "legal_corpus")
EMBED_MODEL = data.get("EMBED_MODEL", "nomic-embed-text")
LLM_MODEL = data.get("LLM_MODEL", "llama3.2:3b")
TOP_K = data.get("TOP_K", 5)


def get_collection():
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_collection(COLLECTION_NAME)


def detect_compliances(question: str) -> list[str]:
    q = question.lower()
    found = []

    if re.search(r"\bgdpr\b", q):
        found.append("GDPR")

    if re.search(r"\bcoppa\b", q):
        found.append("COPPA")

    return found


def retrieve_context(question: str, top_k: int = TOP_K):
    embedder = OllamaEmbeddings(model=EMBED_MODEL)
    collection = get_collection()

    compliances = detect_compliances(question)
    query_vector = embedder.embed_query(question)

    query_kwargs = {
        "query_embeddings": [query_vector],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"]
    }

    if len(compliances) == 1:
        query_kwargs["where"] = {"compliance": compliances[0]}
    elif len(compliances) > 1:
        query_kwargs["where"] = {"compliance": {"$in": compliances}}

    results = collection.query(**query_kwargs)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    blocks = []
    sources = []

    for i, doc in enumerate(documents):
        meta = metadatas[i] if i < len(metadatas) else {}
        dist = distances[i] if i < len(distances) else None

        source = meta.get("source", "desconocido")
        chunk = meta.get("chunk", "N/A")
        compliance = meta.get("compliance", "UNKNOWN")

        blocks.append(
            f"[Fuente: {source} | Compliance: {compliance} | Chunk: {chunk} | Distancia: {dist}]\n{doc}"
        )

        sources.append(
            f"- {source} | compliance={compliance} | chunk={chunk} | distance={dist}"
        )

    context = "\n\n---\n\n".join(blocks)
    return context, sources, compliances


def build_prompt(question: str, context: str, compliances: list[str]) -> str:
    if compliances:
        scope = ", ".join(compliances)
    else:
        scope = "sin filtro específico"

    return f"""
Eres un asistente legal con RAG.

Instrucciones:
- Responde solo con base en el contexto recuperado.
- Si la respuesta no está en el contexto, di: "No encontré esa información en la base documental."
- Si la pregunta menciona varias normativas, compara únicamente esas normativas.
- No inventes información.

Normativas objetivo:
{scope}

Contexto:
{context}

Pregunta:
{question}

Respuesta:
""".strip()


def ask_rag(question: str):
    context, sources, compliances = retrieve_context(question)

    llm = ChatOllama(model=LLM_MODEL)
    prompt = build_prompt(question, context, compliances)
    response = llm.invoke(prompt)

    print("\n=== COMPLIANCES DETECTADOS ===")
    print(", ".join(compliances) if compliances else "Ninguno explícito")

    print("\n=== FUENTES ===")
    for s in sources:
        print(s)

    print("\n=== RESPUESTA ===")
    print(response.content)
    return response.content


def main():
    print("RAG por compliance (escribe 'salir' para terminar)\n")

    while True:
        question = input("Pregunta: ").strip()

        if not question:
            continue

        if question.lower() in {"salir", "exit", "quit"}:
            break

        try:
            ask_rag(question)
        except Exception as e:
            print(f"\n[ERROR] {e}\n")


if __name__ == "__main__":
    main()