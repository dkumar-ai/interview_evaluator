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


def evaluate_interview(conversation):

    transcript = "\n\n".join(
        [
            f"Question: {item['question']}\nAnswer: {item['answer']}"
            for item in conversation
        ]
    )

    prompt = f"""
You are an expert interview evaluator.

Analyze the interview transcript.

Return ONLY valid JSON.

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
    "summary": ""
}}

Rules:
- All scores must be integers between 0 and 100.
- Return ONLY JSON.
- Do not return markdown.

Interview Transcript:

{transcript}
"""

    try:

        response = model.generate_content(prompt)

        text = response.text.strip()
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

        print("\n" + "=" * 50)
        print("RAW GEMINI RESPONSE")
        print("=" * 50)
        print(text)
        print("=" * 50)

        report = json.loads(text)

        # Handle old Gemini schema if returned
        if "technical_score" in report:

            technical = int(report.get("technical_score", 3)) * 20
            communication = int(report.get("communication_score", 3)) * 20
            confidence = int(report.get("confidence_score", 3)) * 20
            problem_solving = int(report.get("problem_solving_score", 3)) * 20
            readiness = int(report.get("overall_readiness", 3)) * 20

            report = {
                "readiness_score": readiness,
                "rubric_scores": {
                    "clarity_structure": communication,
                    "technical_depth": technical,
                    "confidence": confidence,
                    "storytelling": communication,
                    "question_handling": problem_solving
                },
                "strengths": report.get("strengths", []),
                "gaps": report.get("weaknesses", []),
                "summary": report.get("summary", "")
            }

        readiness = int(
            report.get(
                "readiness_score",
                70
            )
        )

        if "rubric_scores" not in report:

            report["rubric_scores"] = {
                "clarity_structure": readiness,
                "technical_depth": readiness,
                "confidence": readiness,
                "storytelling": readiness,
                "question_handling": readiness
            }

        report.setdefault("strengths", [])
        report.setdefault("gaps", [])
        report.setdefault("summary", "")

        return report

    except Exception as e:

        print("EVALUATOR ERROR:", str(e))

        return {
            "readiness_score": 70,
            "rubric_scores": {
                "clarity_structure": 70,
                "technical_depth": 70,
                "confidence": 70,
                "storytelling": 70,
                "question_handling": 70
            },
            "strengths": [
                "Basic interview responses available"
            ],
            "gaps": [
                f"Evaluation error: {str(e)}"
            ],
            "summary": "Fallback evaluation generated due to parsing error."
        }