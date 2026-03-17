# Pediatric Medical RAG System

Mini proyecto de **Procesamiento de Lenguaje Natural (PLN)** que implementa un sistema **Retrieval-Augmented Generation (RAG)** para consultas médicas en pediatría utilizando **Ollama + ChromaDB**.

El sistema procesa documentos médicos, construye una base vectorial y permite realizar consultas semánticas sobre el contenido.

---

# Requisitos

* Python **3.10+**
* Ollama instalado

https://ollama.com/

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

# Configuración

Toda la configuración del sistema se encuentra en:

```
config.json
```

---

# Construcción del Pipeline

Para procesar los documentos y construir la base vectorial ejecutar:

```bash
python -m src.run_pipeline
```

Este script ejecuta automáticamente:

1. extracción de texto
2. limpieza del documento
3. construcción de embeddings
4. creación de la base vectorial

---

# Probar el Sistema RAG

Para realizar pruebas del sistema de recuperación y generación:

```bash
python -m src.test_rag
```

Esto iniciará una interfaz de prueba para realizar preguntas al sistema.

Ejemplo:

```
Pregunta: ¿Qué es la fontanela en un recién nacido?
```

El sistema devolverá una respuesta basada únicamente en la base médica.

---

# API de Consulta

El sistema incluye una **API para realizar consultas al RAG**.

Ejecutar la API:

```bash
uvicorn src.api.rag_api:app --reload
```

La API estará disponible en:

```
http://localhost:8000
```

Documentación interactiva:

```
http://localhost:8000/docs
```

---

# Endpoint principal

POST `/ask`

Request:

```json
{
  "question": "¿Qué es la fontanela en un bebé?"
}
```

Response:

```json
{
  "answer": "La fontanela es..."
}
```

---

# Autor

Mini Proyecto – Procesamiento de Lenguaje Natural

Diego Botto
Hailton Amaya
