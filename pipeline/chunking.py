import json
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List



data = json.loads("{}")

try:
    with open("var.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    print("File data =", data)
except FileNotFoundError:
    print("Archivo var.json no existe, se usarán valores por defecto")

CHUNK_SIZE = data.get("CHUNK_SIZE", 1000)
CHUNK_OVERLAP = data.get("CHUNK_OVERLAP", 200)


def get_splitter() -> RecursiveCharacterTextSplitter:
    # Devuelve el splitter configurado
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )


def chunk_text(text: str) -> List[str]:
    # Divide el texto en fragmentos semánticos.
    print("[INFO] Generando chunks...")
    splitter = get_splitter()
    chunks = splitter.split_text(text)

    print(f"[INFO] Chunks creados: {len(chunks)}")
    return chunks


def process_file(input_path: Path) -> List[str]:
    # Lee archivo y devuelve chunks.
    if not input_path.exists():
        raise FileNotFoundError(f"No existe: {input_path}")

    print(f"[INFO] Leyendo archivo: {input_path}")
    text = input_path.read_text(encoding="utf-8")

    return chunk_text(text)


def main():
    input_path = Path("data/processed/gdpr_clean.txt")
    chunks = process_file(input_path)

    print(f"[INFO] Primer chunk:\n{chunks[0][:300]}")


if __name__ == "__main__":
    main()