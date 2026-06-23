import re
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


# ─── Deterministic enrichment (no LLM needed) ────────────────────────────────

def _derive_performance_label(readiness_score: int) -> str:
    if readiness_score >= 90:
        return "Excellent Performance"
    elif readiness_score >= 80:
        return "Strong Performance"
    elif readiness_score >= 70:
        return "Good Performance"
    elif readiness_score >= 60:
        return "Needs Improvement"
    else:
        return "Requires Practice"


def _derive_presence(rubric: dict, readiness_score: int) -> tuple[int, str]:
    presence_score = int(rubric.get("confidence", readiness_score))
    if presence_score >= 85:
        presence_summary = "Confident delivery and professional communication."
    elif presence_score >= 70:
        presence_summary = "Good communication with room for stronger delivery."
    else:
        presence_summary = "Communication confidence can be improved."
    return presence_score, presence_summary


def _enrich_report(report: dict) -> dict:
    """
    Adds performance_label, interview_presence, and coach_moments to the
    report dict in-place and returns it. Called after every Gemini parse
    and also applied to the fallback payload.
    """
    readiness = int(report.get("readiness_score", 70))
    rubric    = report.get("rubric_scores", {})

    # 1. performance_label
    report["performance_label"] = _derive_performance_label(readiness)

    # 2. interview_presence  (score + one-line summary as a nested object)
    presence_score, presence_summary = _derive_presence(rubric, readiness)
    report["interview_presence"] = {
        "score":   presence_score,
        "summary": presence_summary
    }

    # 3. coach_moments — Gemini is asked to return these directly (see prompt).
    #    If missing or malformed, fall back to deriving from gaps so the
    #    field is always present.
    if not isinstance(report.get("coach_moments"), list) or len(report.get("coach_moments", [])) == 0:
        coach_moments = []
        for idx, gap in enumerate(report.get("gaps", [])[:3], start=1):
            coach_moments.append({
                "title":    gap[:60],
                "feedback": gap
            })
        report["coach_moments"] = coach_moments

    return report


def _clean_gemini_json(text: str) -> str:
    """
    Sanitizes raw Gemini output before JSON parsing.
    Handles the most common failure modes: markdown fences,
    control characters, trailing commas, and newlines inside strings.
    """
    # Strip markdown fences
    text = text.replace("```json", "").replace("```", "").strip()

    # Strip control characters that break JSON (except \n \r \t which are valid)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)

    # Remove trailing commas before } or ] (invalid JSON)
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)

    return text


# ─── Main evaluation function ─────────────────────────────────────────────────

def evaluate_interview(conversation):

    transcript = "\n\n".join(
        [
            f"Question: {item['question']}\nAnswer: {item['answer']}"
            for item in conversation
        ]
    )

    prompt = f"""
You are an expert interview evaluator.

Analyze the interview transcript and return ONLY valid JSON matching the schema below.

Required Schema:

{{
    "readiness_score": 0,
    "rubric_scores": {{
        "clarity_structure": 0,
        "technical_depth": 0,
        "confidence": 0,
        "storytelling": 0,
        "question_handling": 0
    }},
    "strengths": [],
    "gaps": [],
    "summary": "",
    "coach_moments": [
        {{
            "title": "Short label for this coaching point (max 60 chars)",
            "feedback": "Specific, actionable coaching advice for the candidate"
        }}
    ]
}}

Rules:
- All scores must be integers between 0 and 100.
- coach_moments must have 2 to 4 items. Each must be specific and actionable,
  not a repeat of gaps. Focus on HOW the candidate can improve delivery,
  structure, or depth.
- The summary field must be a single line string with no newline characters inside it.
- Do not use line breaks inside any string value in the JSON.
- Return ONLY JSON. Do not return markdown or any text outside the JSON object.

Interview Transcript:

{transcript}
"""

    try:

        response = model.generate_content(prompt)

        text = _clean_gemini_json(response.text)

        print("\n" + "=" * 50)
        print("RAW GEMINI RESPONSE")
        print("=" * 50)
        print(text)
        print("=" * 50)

        report = json.loads(text)

        # ── Handle legacy Gemini schema (old 1-5 scale responses) ──────────
        if "technical_score" in report:

            technical       = int(report.get("technical_score",       3)) * 20
            communication   = int(report.get("communication_score",   3)) * 20
            confidence      = int(report.get("confidence_score",      3)) * 20
            problem_solving = int(report.get("problem_solving_score", 3)) * 20
            readiness       = int(report.get("overall_readiness",     3)) * 20

            report = {
                "readiness_score": readiness,
                "rubric_scores": {
                    "clarity_structure": communication,
                    "technical_depth":   technical,
                    "confidence":        confidence,
                    "storytelling":      communication,
                    "question_handling": problem_solving
                },
                "strengths":     report.get("strengths",  []),
                "gaps":          report.get("weaknesses", []),
                "summary":       report.get("summary",    ""),
                "coach_moments": []  # filled by _enrich_report fallback
            }

        # ── Ensure all base fields exist ────────────────────────────────────
        readiness = int(report.get("readiness_score", 70))

        if "rubric_scores" not in report:
            report["rubric_scores"] = {
                "clarity_structure": readiness,
                "technical_depth":   readiness,
                "confidence":        readiness,
                "storytelling":      readiness,
                "question_handling": readiness
            }

        report.setdefault("strengths",     [])
        report.setdefault("gaps",          [])
        report.setdefault("summary",       "")
        report.setdefault("coach_moments", [])

        # ── Add derived design fields ───────────────────────────────────────
        report = _enrich_report(report)

        return report

    except Exception as e:

        print("EVALUATOR ERROR:", str(e))

        fallback = {
            "readiness_score": 70,
            "rubric_scores": {
                "clarity_structure": 70,
                "technical_depth":   70,
                "confidence":        70,
                "storytelling":      70,
                "question_handling": 70
            },
            "strengths": [
                "Basic interview responses available"
            ],
            "gaps": [
                f"Evaluation error: {str(e)}"
            ],
            "summary": "Fallback evaluation generated due to parsing error.",
            "coach_moments": [
                {
                    "title":    "Review your answer structure",
                    "feedback": "Use the STAR method (Situation, Task, Action, Result) to frame answers clearly."
                },
                {
                    "title":    "Strengthen technical depth",
                    "feedback": "Back each technical claim with a concrete example or metric from past experience."
                }
            ]
        }

        return _enrich_report(fallback)
