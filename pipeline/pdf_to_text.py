from pathlib import Path
import sys
import pymupdf as fitz


def extract_pdf_text(pdf_path: Path) -> str:
    # Extrae texto preservando layout del PDF

    print(f"[INFO] Leyendo PDF: {pdf_path.name}")

    doc = fitz.open(pdf_path)
    text_pages = []

    for page in doc:
        blocks = page.get_text("blocks")

        page_text = ""
        for block in sorted(blocks, key=lambda b: (b[1], b[0])):
            page_text += block[4].strip() + "\n"

        text_pages.append(page_text)

    return "\n".join(text_pages)


def save_text(text: str, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    print(f"[OK] Guardado: {output_path.name}")


def process_pdf(pdf_path: Path, output_dir: Path):
    # Procesa un solo PDF
    text = extract_pdf_text(pdf_path)
    output_path = output_dir / (pdf_path.stem + ".txt")
    save_text(text, output_path)


def process_folder(folder_path: Path, output_dir: Path):
    # Procesa todos los PDFs dentro de una carpeta 

    pdf_files = list(folder_path.rglob("*.pdf"))

    if not pdf_files:
        print("[WARN] No se encontraron PDFs en la carpeta")
        return

    print(f"[INFO] PDFs encontrados: {len(pdf_files)}\n")

    for pdf in pdf_files:
        process_pdf(pdf, output_dir)

    print("\n[OK] Conversión masiva completada")


def main():

    if len(sys.argv) != 2:
        print("Uso:")
        print("  python -m pipeline.pdf_to_text <archivo.pdf>")
        print("  python -m pipeline.pdf_to_text <carpeta>")
        return

    input_path = Path(sys.argv[1])
    output_dir = Path("data/raw")

    if not input_path.exists():
        print("Ruta no existe")
        return

    # Caso 1: archivo único
    if input_path.is_file() and input_path.suffix.lower() == ".pdf":
        process_pdf(input_path, output_dir)

    # Caso 2: carpeta completa
    elif input_path.is_dir():
        process_folder(input_path, output_dir)

    else:
        print("Debe ser un archivo PDF o una carpeta que contenga PDFs")


if __name__ == "__main__":
    main()