from pathlib import Path
import pymupdf as fitz
from typing import List
from src.utils.config_loader import load_config


config = load_config()

RAW_DATA_DIR = Path(config["paths"]["raw_data"])


def extract_pdf_text(pdf_path: Path) -> str:
    """
    Extrae el texto de un PDF preservando el layout aproximado.
    """

    print(f"[INFO] Leyendo PDF: {pdf_path.name}")

    text_pages: List[str] = []

    with fitz.open(pdf_path) as doc:
        for page in doc:
            blocks = page.get_text("blocks")

            page_text = ""
            for block in sorted(blocks, key=lambda b: (b[1], b[0])):
                page_text += block[4].strip() + "\n"

            text_pages.append(page_text)

    return "\n".join(text_pages)


def save_text(text: str, output_path: Path) -> None:
    """
    Guarda texto en archivo .txt
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")

    print(f"[OK] Guardado: {output_path}")


def process_pdf(pdf_path: Path, output_dir: Path) -> Path:
    """
    Procesa un único PDF y devuelve la ruta del txt generado.
    """

    text = extract_pdf_text(pdf_path)

    output_path = output_dir / f"{pdf_path.stem}.txt"

    save_text(text, output_path)

    return output_path


def process_folder(folder_path: Path, output_dir: Path) -> List[Path]:
    """
    Procesa todos los PDFs dentro de una carpeta.
    """

    pdf_files = list(folder_path.rglob("*.pdf"))

    if not pdf_files:
        print("[WARN] No se encontraron PDFs")
        return []

    print(f"[INFO] PDFs encontrados: {len(pdf_files)}")

    results = []

    for pdf in pdf_files:
        result = process_pdf(pdf, output_dir)
        results.append(result)

    print("[OK] Conversión masiva completada")

    return results


def run(input_path: Path) -> None:
    """
    Punto de entrada para el pipeline
    """

    if not input_path.exists():
        raise FileNotFoundError(f"No existe la ruta: {input_path}")

    if input_path.is_file() and input_path.suffix.lower() == ".pdf":
        process_pdf(input_path, RAW_DATA_DIR)

    elif input_path.is_dir():
        process_folder(input_path, RAW_DATA_DIR)

    else:
        raise ValueError("Debe ser un archivo PDF o una carpeta con PDFs")