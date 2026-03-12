from pathlib import Path
import chromadb
import json
from langchain_ollama import OllamaEmbeddings

from pipeline.chunking import chunk_text

data = json.loads("{}")  

try:
    with open("var.json", "r", encoding="utf-8") as file:
        data = json.load(file)

except FileNotFoundError:
    print("Archivo var.json no existe, se usarán valores por defecto")

except json.JSONDecodeError:
    print("Archivo var.json es inválido, se usarán valores por defecto")


PROCESSED_DIR = Path(data.get("PROCESSED_DIR", "data/processed"))
DB_PATH = data.get("DB_PATH", "data/chroma_db")
COLLECTION_NAME = data.get("COLLECTION_NAME", "legal_corpus")




def detect_compliance_from_filename(filename: str) -> str:
    name = filename.lower()

    if "gdpr" in name or "32016r0679" in name:
        return "GDPR"
    if "coppa" in name:
        return "COPPA"

    return "UNKNOWN"


def build_vector_database():
    if not PROCESSED_DIR.exists():
        raise FileNotFoundError("No existe la carpeta data/processed")

    files = list(PROCESSED_DIR.glob("*_clean.txt"))

    if not files:
        raise FileNotFoundError("No hay archivos limpios para indexar")

    print(f"[INFO] Documentos encontrados: {len(files)}")

    embedder = OllamaEmbeddings(model="nomic-embed-text")
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(COLLECTION_NAME)

    total = 0

    for file in files:
        compliance = detect_compliance_from_filename(file.name)
        print(f"\n[DOC] {file.name} | compliance={compliance}")

        text = file.read_text(encoding="utf-8")
        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            vector = embedder.embed_query(chunk)

            collection.add(
                documents=[chunk],
                embeddings=[vector],
                ids=[f"{file.stem}_chunk_{i}"],
                metadatas=[{
                    "source": file.name,
                    "chunk": i,
                    "compliance": compliance
                }]
            )
            total += 1

    print(f"\n[OK] Base vectorial creada con {total} chunks")


def main():
    build_vector_database()


if __name__ == "__main__":
    main()