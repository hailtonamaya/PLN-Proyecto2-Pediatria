from pathlib import Path
import re
from typing import List
from src.utils.config_loader import load_config


config = load_config()

RAW_DIR = Path(config["paths"]["raw_data"])
PROCESSED_DIR = Path(config["paths"]["processed_data"])


def normalize_text(text: str) -> str:
    """
    Normaliza texto extraído de PDFs médicos.
    """

    print("[INFO] Normalizando texto...")

    # unir palabras separadas por salto de línea con guion
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)

    # reemplazar saltos múltiples
    text = re.sub(r'\n{3,}', '\n\n', text)

    # eliminar espacios duplicados
    text = re.sub(r'[ \t]+', ' ', text)

    # eliminar espacios al inicio y final
    text = text.strip()

    return text


def remove_page_numbers(text: str) -> str:
    """
    Elimina números de página aislados típicos de libros.
    """

    print("[INFO] Eliminando números de página...")

    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)

    return text


def remove_short_lines(text: str) -> str:
    """
    Elimina líneas extremadamente cortas que suelen ser ruido.
    """

    print("[INFO] Eliminando líneas cortas...")

    lines = text.split("\n")

    cleaned = []

    for line in lines:
        line = line.strip()

        if len(line) <= 2:
            continue

        cleaned.append(line)

    return "\n".join(cleaned)


def clean_text_pipeline(text: str) -> str:
    """
    Pipeline de limpieza completo.
    """

    text = normalize_text(text)
    text = remove_page_numbers(text)
    text = remove_short_lines(text)

    return text


def clean_single_file(input_path: Path, output_dir: Path) -> Path:
    """
    Limpia un archivo txt.
    """

    print(f"\n[FILE] {input_path.name}")

    raw = input_path.read_text(encoding="utf-8")

    clean = clean_text_pipeline(raw)

    output_path = output_dir / f"{input_path.stem}_clean.txt"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(clean, encoding="utf-8")

    print(f"[OK] Guardado: {output_path}")

    return output_path


def process_folder(input_dir: Path, output_dir: Path) -> List[Path]:
    """
    Limpia todos los txt dentro de una carpeta.
    """

    txt_files = list(input_dir.rglob("*.txt"))

    if not txt_files:
        print("[WARN] No hay archivos .txt en la carpeta")
        return []

    print(f"[INFO] Archivos encontrados: {len(txt_files)}")

    results = []

    for txt in txt_files:
        result = clean_single_file(txt, output_dir)
        results.append(result)

    print("[OK] Limpieza masiva completada")

    return results


def run():
    """
    Punto de entrada del pipeline de limpieza.
    """

    if not RAW_DIR.exists():
        raise FileNotFoundError("No existe la carpeta data/raw")

    return process_folder(RAW_DIR, PROCESSED_DIR)