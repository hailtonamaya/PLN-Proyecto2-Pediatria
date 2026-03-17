from fastapi import FastAPI
from pydantic import BaseModel

from src.RAG.rag_pipeline import ask

app = FastAPI(
    title="Pediatria RAG API",
    description="API para consultar el sistema RAG de pediatría",
    version="1.0"
)


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str


@app.get("/")
def root():
    return {"message": "RAG API funcionando"}


@app.post("/ask", response_model=AnswerResponse)
def ask_question(data: QuestionRequest):

    try:
        response = ask(data.question)

        return {
            "answer": response
        }

    except Exception as e:
        return {
            "answer": f"Error: {str(e)}"
        }