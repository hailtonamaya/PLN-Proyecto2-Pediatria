from pathlib import Path
from typing import List
import chromadb
from langchain_ollama import OllamaEmbeddings

from src.utils.config_loader import load_config
from src.pipeline.chunking import chunk_file


config = load_config()

PROCESSED_DIR = Path(config["paths"]["processed_data"])
VECTOR_DB_PATH = config["paths"]["vector_db"]

COLLECTION_NAME = config["vector_database"]["collection_name"]

EMBED_MODEL = config["models"]["embedding_model"]


def get_embedding_model():
    """
    Inicializa modelo de embeddings de Ollama
    """

    print(f"[INFO] Usando embedding model: {EMBED_MODEL}")

    return OllamaEmbeddings(model=EMBED_MODEL)


def get_chroma_collection():
    """
    Inicializa cliente ChromaDB
    """

    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    return collection


def load_documents() -> List[Path]:
    """
    Obtiene archivos limpios para indexar
    """

    if not PROCESSED_DIR.exists():
        raise FileNotFoundError("No existe data/processed")

    files = list(PROCESSED_DIR.glob("*_clean.txt"))

    if not files:
        raise FileNotFoundError("No hay archivos para indexar")

    print(f"[INFO] Documentos encontrados: {len(files)}")

    return files


def build_vector_database():
    """
    Construye base vectorial completa
    """

    files = load_documents()

    embedder = get_embedding_model()
    collection = get_chroma_collection()

    total_chunks = 0

    for file in files:

        print(f"\n[DOC] {file.name}")

        chunks = chunk_file(file)

        embeddings = embedder.embed_documents(chunks)

        ids = [f"{file.stem}_chunk_{i}" for i in range(len(chunks))]

        metadatas = [
            {
                "source": file.name,
                "chunk": i
            }
            for i in range(len(chunks))
        ]

        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )

        total_chunks += len(chunks)

        print(f"[INFO] Chunks indexados: {len(chunks)}")

    print(f"\n[OK] Base vectorial creada con {total_chunks} chunks")


def run():
    """
    Punto de entrada para pipeline
    """

    build_vector_database()