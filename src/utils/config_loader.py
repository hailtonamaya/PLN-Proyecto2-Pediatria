import json
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parents[2]  / "config.json"


def load_config() -> dict:
    """
    Carga el archivo config.json del proyecto.
    """

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró config.json en: {CONFIG_PATH}"
        )

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)

    except json.JSONDecodeError as e:
        raise ValueError(f"config.json inválido: {e}")

    return config