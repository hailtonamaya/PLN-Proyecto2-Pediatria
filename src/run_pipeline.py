from pathlib import Path

from src.pipeline.pdf_to_text import run as extract_pdfs
from src.pipeline.clean_text import run as clean_text
from src.pipeline.chunking import run as generate_chunks
from src.pipeline.build_vector_db import run as build_db
from src.utils.config_loader import load_config

config = load_config()


def main():

    print("\n========== PIPELINE RAG PEDIATRÍA ==========\n")

    path = config["paths"]["raw_data"]

    print("1️⃣ Extrayendo texto de PDFs...")
    extract_pdfs(Path(path))

    print("\n2️⃣ Limpiando texto...")
    clean_text()

    print("\n3️⃣ Generando chunks...")
    generate_chunks()

    print("\n4️⃣ Construyendo base vectorial...")
    build_db()

    print("\n✅ Pipeline completado")


if __name__ == "__main__":
    main()