import os

BACKEND_AUTH_TOKEN = os.getenv("BACKEND_AUTH_TOKEN")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any

import requests

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

BACKEND_URL = "https://qp158oafxk.execute-api.ap-south-1.amazonaws.com"


# ==========================================================
# REQUEST MODELS
# ==========================================================

class QAPair(BaseModel):
    question: str
    answer: str


class EvaluateRequest(BaseModel):

    user_id: Union[str, int]
    session_id: Optional[int] = None

    role: Optional[str] = None
    session_type: Optional[str] = None
    round_type: Optional[str] = None
    company_tier: Optional[str] = None
    icp: Optional[str] = None

    transcript: Optional[List[QAPair]] = None

    signal_snapshots: Optional[List[Dict[str, Any]]] = None

    audio_s3_key: Optional[str] = None

    onboarding_summary: Optional[Dict[str, Any]] = None

    session_duration_seconds: Optional[int] = None
    question_count: Optional[int] = None


# ==========================================================
# BACKEND SAVE
# ==========================================================

def save_evaluation_to_backend(
    session_id: int,
    report: dict
):

    rubric = report.get("rubric_scores", {})
    presence = report.get("interview_presence", {})

    payload = {
        "session_id": session_id,

        "overall_score": report.get(
            "readiness_score",
            0
        ),

        "performance_label": report.get(
            "performance_label",
            ""
        ),

        "skill_evaluation": {
            "clarity": rubric.get(
                "clarity_structure",
                0
            ),
            "technical": rubric.get(
                "technical_depth",
                0
            ),
            "confidence": rubric.get(
                "confidence",
                0
            ),
            "storytelling": rubric.get(
                "storytelling",
                0
            ),
            "question_handling": rubric.get(
                "question_handling",
                0
            )
        },

        "presence_score": presence.get(
            "score",
            0
        ),

        "presence_summary": presence.get(
            "summary",
            ""
        ),

        "strengths": report.get(
            "strengths",
            []
        ),

        "improvement_areas": report.get(
            "gaps",
            []
        ),

        "coach_moments": report.get(
            "coach_moments",
            []
        ),

        "summary": report.get(
            "summary",
            ""
        )
    }

    print("\n==============================")
    print("BACKEND SAVE")
    print("==============================")
    print(payload)

    headers = {
        "Authorization": f"Bearer {BACKEND_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    print("AUTH TOKEN PRESENT:", bool(BACKEND_AUTH_TOKEN))
    response = requests.post(
        f"{BACKEND_URL}/interview/evaluation",
        json=payload,
        headers=headers,
        timeout=30
    )

    print(
        f"[BACKEND] STATUS = {response.status_code}"
    )

    print(
        f"[BACKEND] BODY = {response.text}"
    )

    response.raise_for_status()

    return response.json()


# ==========================================================
# HEALTH
# ==========================================================

@app.get("/")
def health():

    return {
        "status": "ok",
        "service": "interview-evaluator"
    }


# ==========================================================
# MAIN EVALUATION
# ==========================================================

@app.post("/evaluate")
def evaluate(req: EvaluateRequest):

    print("\n==============================")
    print("REQUEST RECEIVED")
    print("==============================")
    print(req.model_dump())

    # --------------------------------
    # Primary path
    # Lambda sends transcript
    # --------------------------------

    if req.transcript and len(req.transcript) > 0:

        conversation = [
            {
                "question": qa.question,
                "answer": qa.answer
            }
            for qa in req.transcript
        ]

        print(
            f"[EVAL] Using payload transcript "
            f"({len(conversation)} Q&A pairs)"
        )

    # --------------------------------
    # Fallback path
    # Streamlit / legacy Pinecone
    # --------------------------------

    else:

        print(
            f"[EVAL] Transcript missing."
        )

        print(
            f"[EVAL] Fetching from Pinecone "
            f"user={req.user_id}"
        )

        conversation = get_interview_data(
            str(req.user_id)
        )

    if not conversation:

        return {
            "status": "error",
            "message": "No interview data found"
        }

    print(
        f"[EVAL] Starting evaluation "
        f"for session={req.session_id}"
    )

    report = evaluate_interview(
        conversation
    )

    mastery = calculate_mastery(
        report
    )

    backend_response = None

    if req.session_id:

        try:

            backend_response = save_evaluation_to_backend(
                req.session_id,
                report
            )

            print(
                f"[BACKEND] Evaluation saved "
                f"for session={req.session_id}"
            )

        except Exception as e:

            print(
                f"[BACKEND ERROR] {str(e)}"
            )

            return {
                "status": "error",
                "message": f"Failed to save evaluation to backend: {str(e)}"
            }

    return {
        "status": "success",
        "user_id": str(req.user_id),
        "session_id": req.session_id,
        "mastery": mastery,
        "report": report,
        "backend_response": backend_response
    }
