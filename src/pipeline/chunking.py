from pathlib import Path
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.utils.config_loader import load_config


config = load_config()

CHUNK_SIZE = config["chunking"]["chunk_size"]
CHUNK_OVERLAP = config["chunking"]["chunk_overlap"]

PROCESSED_DIR = Path(config["paths"]["processed_data"])


def get_splitter() -> RecursiveCharacterTextSplitter:
    """
    Configura el splitter optimizado para texto médico.
    """

    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n\n",   # párrafos
            "\n",     # líneas
            ". ",     # oraciones
            " ",      # palabras
        ]
    )


def chunk_text(text: str) -> List[str]:
    """
    Divide texto en chunks semánticos.
    """

    print("[INFO] Generando chunks...")

    splitter = get_splitter()

    chunks = splitter.split_text(text)

    print(f"[INFO] Chunks creados: {len(chunks)}")

    return chunks


def chunk_file(input_path: Path) -> List[str]:
    """
    Lee archivo y genera chunks.
    """

    if not input_path.exists():
        raise FileNotFoundError(f"No existe: {input_path}")

    print(f"[INFO] Procesando: {input_path.name}")

    text = input_path.read_text(encoding="utf-8")

    return chunk_text(text)


def process_folder(input_dir: Path) -> List[str]:
    """
    Genera chunks para todos los archivos de una carpeta.
    """

    txt_files = list(input_dir.rglob("*_clean.txt"))

    if not txt_files:
        print("[WARN] No se encontraron archivos limpios")
        return []

    print(f"[INFO] Archivos encontrados: {len(txt_files)}")

    all_chunks = []

    for txt in txt_files:
        chunks = chunk_file(txt)
        all_chunks.extend(chunks)

    print(f"[OK] Total de chunks generados: {len(all_chunks)}")

    return all_chunks


def run() -> List[str]:
    """
    Punto de entrada del pipeline.
    """

    if not PROCESSED_DIR.exists():
        raise FileNotFoundError("No existe data/processed")

    return process_folder(PROCESSED_DIR)