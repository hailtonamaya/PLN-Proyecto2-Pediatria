from pathlib import Path
import re


def normalize_text(text: str) -> str:
    print("[INFO] Normalizando texto...")

    # unir palabras con guion de salto de línea
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)

    # reemplazar saltos múltiples
    text = re.sub(r'\n{2,}', '\n\n', text)

    # eliminar espacios duplicados
    text = re.sub(r'[ \t]+', ' ', text)

    return text

def remove_headers_footers(text: str) -> str:
    print("[INFO] Eliminando encabezados y footers...")

    # remover líneas tipo: 4.5.2016
    text = re.sub(r'\n\d{1,2}\.\d{1,2}\.\d{4}\s*\n', '\n', text)

    # remover líneas tipo: L 119/33
    text = re.sub(r'\nL\s\d+/\d+\s*\n', '\n', text)

    # remover línea "EN"
    text = re.sub(r'\nEN\s*\n', '\n', text)

    text = re.sub(r'Official Journal of the European Union.*', '', text)

    text = re.sub(r'\d+\.\d+\.\d+\sL\s\d+/\d+', '', text)

    return text

def remove_recitals(text: str) -> str:
    print("[INFO] Eliminando recitals...")

    match = re.search(r'CHAPTER\s+I', text)
    if not match:
        print("[WARN] No se encontró CHAPTER I")
        return text

    return text[match.start():]



def clean_single_file(input_path: Path, output_dir: Path):
    print(f"\n[FILE] {input_path.name}")

    raw = input_path.read_text(encoding="utf-8")

    clean = normalize_text(raw)
    clean = remove_headers_footers(clean)
    clean = remove_recitals(clean)

    output_path = output_dir / f"{input_path.stem}_clean.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(clean, encoding="utf-8")

    print(f"[OK] Guardado: {output_path.name} ({len(clean)} chars)")


def process_folder(input_dir: Path, output_dir: Path):
    
    txt_files = list(input_dir.rglob("*.txt"))

    if not txt_files:
        print("[WARN] No hay archivos .txt en la carpeta")
        return

    print(f"[INFO] Archivos encontrados: {len(txt_files)}\n")

    for txt in txt_files:
        clean_single_file(txt, output_dir)

    print("\n[OK] Limpieza masiva completada")


def main():

    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "Data"

    input_dir = DATA_DIR / "raw"
    output_dir = DATA_DIR / "processed"

    if not input_dir.exists():
        print("No existe data/raw")
        return

    if not input_dir.exists():
        print("No existe data/raw")
        return

    process_folder(input_dir, output_dir)


if __name__ == "__main__":
    main()