import streamlit as st

import os
import requests


st.set_page_config(
    page_title="VIDYA Interview Evaluator",
    page_icon="🎯",
    layout="wide"
)

BACKEND_URL = "https://qp158oafxk.execute-api.ap-south-1.amazonaws.com"

JWT_TOKEN = os.getenv("BACKEND_AUTH_TOKEN")

st.markdown(
    """
    <style>

    .block-container{
        padding-top:1rem;
        padding-bottom:1rem;
    }

    div[data-testid="stMetric"]{
        border:1px solid #262730;
        border-radius:12px;
        padding:10px;
        background:#111827;
    }

    .transcript-box{
        height:650px;
        overflow-y:auto;
        border:1px solid #262730;
        border-radius:12px;
        padding:16px;
        background:#111827;
    }

    .summary-box{
        border:1px solid #262730;
        border-radius:12px;
        padding:14px;
        background:#111827;
        margin-bottom:12px;
    }

    .question-box{
        border-left:4px solid #7C5CFC;
        padding-left:12px;
        margin-bottom:18px;
    }

    .answer-box{
        margin-left:10px;
        margin-bottom:24px;
        color:#D1D5DB;
    }

    </style>
    """,
    unsafe_allow_html=True
)



query_params = st.query_params

session_id = query_params.get("session_id", "")

if not session_id:

    st.markdown(
        """
        <style>

        .stApp {
            background: #0E1117;
        }

        .entry-box{
            border:1px solid #262730;
            border-radius:12px;
            padding:24px;
            background:#111827;
            margin-bottom:18px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("🎓 VIDYA Interview Evaluator")

    st.markdown(
        "### Enter Session ID"
    )

    st.divider()

    manual_session_id = st.text_input(
        "Session ID"
    )

    if st.button(
        "Load Evaluation",
        type="primary"
    ):

        if manual_session_id:

            st.query_params["session_id"] = manual_session_id
            st.rerun()

        else:

            st.error(
                "Please enter a Session ID"
            )

    st.stop()
with st.spinner(
    "Fetching evaluation..."
):

    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}"
    }

    try:

        response = requests.get(
            f"{BACKEND_URL}/interview/evaluation/{session_id}",
            headers=headers,
            timeout=30
        )

    except requests.exceptions.RequestException as e:

        st.error(f"Unable to connect to backend.\n\n{e}")
        st.stop()

if response.status_code == 404:

    st.error(
        f"No evaluation found for session {session_id}"
    )

    st.stop()

elif response.status_code == 401:

    st.error(
        "Authentication failed."
    )

    st.stop()

elif response.status_code == 403:

    st.error(
        "Authorization failed."
    )

    st.stop()

elif response.status_code != 200:

    st.error(
        response.text
    )

    st.stop()

payload = response.json()

if not payload.get("success", False):
    st.error("Backend returned an unsuccessful response.")
    st.stop()

evaluation = payload["data"]

report = evaluation

readiness_score = report.get("overall_score", 0)

skills = report.get("skill_evaluation", {})

rubric = {
    "clarity_structure": skills.get("clarity", 0),
    "technical_depth": skills.get("technical", 0),
    "confidence": skills.get("confidence", 0),
    "storytelling": skills.get("storytelling", 0),
    "question_handling": skills.get("question_handling", 0)
}

strengths = report.get("strengths", [])

gaps = report.get("improvement_areas", [])

summary = report.get(
    "summary",
    "No summary available."
)

performance_label = report.get(
    "performance_label",
    "Evaluation Available"
)

presence_score = report.get(
    "presence_score",
    0
)

presence_summary = report.get(
    "presence_summary",
    ""
)

coach_moments = report.get(
    "coach_moments",
    []
)

mastery = readiness_score / 100

conversation = []

st.success(
    "Evaluation Loaded Successfully"
)

left_panel, center_panel, right_panel = st.columns(
    [1, 3, 1.5]
)

# =========================
# LEFT PANEL
# =========================

with left_panel:

    st.markdown(
        "## 🎯 VIDYA"
    )

    st.markdown(
        "### Interview Evaluator"
    )

    st.divider()

    st.markdown(
        "#### Current User"
    )

    st.success(
        f"Session {session_id}"
    )

    st.markdown(
        "#### Session"
    )

    session_display = query_params.get(
        "session_id",
        "Unknown"
    )

    st.info(
       str(session_display)
    )


    
    st.divider()

    st.markdown(
        "#### Evaluation Status"
    )

    if readiness_score >= 90:

        st.success(
            "Interview Ready"
        )

    elif readiness_score >= 75:

        st.info(
            "Strong Candidate"
        )

    elif readiness_score >= 60:

        st.warning(
            "Needs Improvement"
        )

    else:

        st.error(
            "Requires Practice"
        )

    st.divider()

    st.markdown(
        "#### Score Snapshot"
    )

    st.write(
        f"Readiness: {readiness_score}/100"
    )

    st.write(
        f"Mastery: {int(mastery * 100)}%"
    )

    st.write(
        f"Strengths: {len(strengths)}"
    )

    st.write(
        f"Gaps: {len(gaps)}"
    )

# =========================
# CENTER PANEL
# =========================

with center_panel:

    st.markdown(
        "## Evaluation Metrics"
    )

    row1 = st.columns(4)

    with row1[0]:

        st.metric(
            "Readiness",
            readiness_score
        )
        st.caption(performance_label)

    with row1[1]:

        st.metric(
            "Clarity",
            rubric.get("clarity_structure", 0)
        )

    with row1[2]:

        st.metric(
            "Technical",
            rubric.get("technical_depth", 0)
        )

    with row1[3]:

        st.metric(
            "Confidence",
            rubric.get("confidence", 0)
        )

    row2 = st.columns(3)

    with row2[0]:

        st.metric(
            "Storytelling",
            rubric.get("storytelling", 0)
        )

    with row2[1]:

        st.metric(
            "Question Handling",
            rubric.get("question_handling", 0)
        )

    with row2[2]:

        st.metric(
            "Mastery",
            f"{int(mastery * 100)}%"
        )

    st.divider()

    with st.spinner("Loading transcript..."):

        transcript_response = requests.get(
            f"https://interviewevaluator-production.up.railway.app/transcript/{session_id}",
            timeout=30
        )

    if transcript_response.status_code == 200:

        transcript = transcript_response.json()["transcript"]

        st.markdown(
            f"## Interview Transcript ({len(transcript)} Questions)"
        )

        transcript_container = st.container(border=True)

        with transcript_container:

            for index, item in enumerate(transcript, start=1):

                st.markdown(
                    f"""
                    <div class='question-box'>
                    <b>Question {index}</b><br><br>
                    {item['question']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class='answer-box'>
                    <b>Answer</b><br><br>
                    {item['answer']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    else:

        st.info("Transcript not available.")

    
# =========================
# RIGHT PANEL
# =========================

with right_panel:

    st.markdown("## Summary")

    st.markdown(
        f"""
        <div class="summary-box">
        {summary}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ── Interview Presence ──────────────────────────────────────────────────
    st.markdown("## Interview Presence")

    st.metric("Presence Score", presence_score)
    st.caption(presence_summary)

    st.divider()

    st.markdown("## Strengths")

    if strengths:
        for item in strengths:
            st.success(item)
    else:
        st.info("No strengths identified.")

    st.divider()

    st.markdown("## Improvement Areas")

    if gaps:
        for item in gaps:
            st.warning(item)
    else:
        st.info("No improvement areas identified.")

    st.divider()

# =========================
# INTERVIEW COACH
# =========================

st.markdown("## Interview Coach")

if coach_moments:

    for moment in coach_moments:

        st.markdown(
            f"""
            **{moment['title']}**

            {moment['feedback']}
            """
        )

else:

    st.info("No coach moments available.")
