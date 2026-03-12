# GDPR Compliance Auditor (Mini Proyecto PLN)

---

## Funcionamiento

El sistema realiza los siguientes pasos:

1. Extrae texto del reglamento en PDF.
2. Limpia el documento jurídico (elimina recitals y normaliza texto).
3. Divide el documento en fragmentos semánticos (chunking).
4. Genera embeddings usando Ollama.
5. Construye una base vectorial persistente con ChromaDB.
6. Permite realizar búsqueda semántica sobre la normativa.

---

## Requisitos

- Python 3.10 o superior
- Ollama instalado  
  https://ollama.com/


## Ejecución paso a paso

### 1️⃣ Convertir PDF a texto

```bash
python -m pipeline.pdf_to_text <ruta_a_archivos>
```

Genera:

```
data/raw/nombre_archivo.txt
```

---

### 2️⃣ Limpiar documento

```bash
python -m pipeline.clean_text
```

Genera:

```
data/processed/nombre_archivo_clean.txt
```

---

### 3️⃣ Construir base vectorial

```bash
python -m pipeline.build_vector_db
```

Esto creará:

```
data/chroma_db/
```

---

### 5️⃣ Probar búsqueda semántica

```bash
python -m pipeline.RAG
```

El sistema devolverá una respuesta segun lo que se le pregunte.

---

## Autor

Mini proyecto – Procesamiento de Lenguaje Natural
By Diego Botto & Hailton Amaya
