from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.pinecone_service import get_interview_data
from services.evaluator import evaluate_interview
from services.mastery import calculate_mastery

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EvaluateRequest(BaseModel):
    user_id: str
    session_id: str = None

@app.get("/")
def health():
    return {"status": "ok", "service": "interview-evaluator"}

@app.post("/evaluate")
def evaluate(req: EvaluateRequest):
    conversation = get_interview_data(req.user_id)
    if not conversation:
        return {"status": "error", "message": "No interview data found"}
    report = evaluate_interview(conversation)
    mastery = calculate_mastery(report)
    return {
        "status": "success",
        "user_id": req.user_id,
        "mastery": mastery,
        "report": report
    }