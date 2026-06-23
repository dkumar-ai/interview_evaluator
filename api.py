from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from services.pinecone_service import get_interview_data, get_evaluation_result
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


class QAPair(BaseModel):
    question: str
    answer: str


class EvaluateRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    transcript: Optional[List[QAPair]] = None


@app.get("/")
def health():
    return {"status": "ok", "service": "interview-evaluator"}


@app.post("/evaluate")
def evaluate(req: EvaluateRequest):

    # Use transcript from frontend if provided
    if req.transcript and len(req.transcript) > 0:
        conversation = [
            {"question": qa.question, "answer": qa.answer}
            for qa in req.transcript
        ]
        print(f"[EVAL] Using frontend transcript — {len(conversation)} Q&A pairs")

    # Fallback to Pinecone
    else:
        print(f"[EVAL] No transcript in request — fetching from Pinecone for user={req.user_id}")
        conversation = get_interview_data(req.user_id)

    if not conversation:
        return {
            "status": "error",
            "message": "No interview data found"
        }

    report  = evaluate_interview(conversation)
    mastery = calculate_mastery(report)

    return {
        "status": "success",
        "user_id": req.user_id,
        "mastery": mastery,
        "report": report
    }


@app.get("/interview/evaluation")
def get_evaluation(user_id: str, session_id: str):

    if not user_id or not session_id:
        raise HTTPException(
            status_code=400,
            detail="user_id and session_id are required"
        )

    result = get_evaluation_result(user_id, session_id)

    # Evaluation exists and is complete
    if result and result["status"] == "completed":
        return {
            "status": "success",
            "user_id": user_id,
            "session_id": session_id,
            "report": result["report"]
        }

    # Lambda triggered but evaluation still running
    if result and result["status"] == "PROCESSING":
        return {
            "status": "PROCESSING",
            "user_id": user_id,
            "session_id": session_id,
            "report": None
        }

    # Lambda failed
    if result and result["status"] == "FAILED":
        return {
            "status": "FAILED",
            "user_id": user_id,
            "session_id": session_id,
            "report": None
        }

    # Nothing found at all
    raise HTTPException(
        status_code=404,
        detail=f"No evaluation found for user_id={user_id} session_id={session_id}"
    )
