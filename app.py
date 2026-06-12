import streamlit as st


from services.pinecone_services import get_interview_data
from services.evaluator import evaluate_interview
from services.mastery import calculate_mastery

st.set_page_config(
    page_title="VIDYA Interview Evaluator",
    page_icon="🎯",
    layout="wide"
)

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

user_id = query_params.get(
    "user_id",
    None
)

if not user_id:

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

    st.title(
        "🎓 VIDYA Interview Evaluator"
    )

    st.markdown(
        "### Select or Enter Interview Details"
    )

    st.divider()

    sessions = get_all_sessions()

    session_options = ["None"] + [
        s["label"] for s in sessions
    ]

    selected_session = st.selectbox(
        "Available Interview Sessions",
        session_options
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        manual_user_id = st.text_input("User ID")

    with col2:
        manual_session_id = st.text_input("Session ID")

    st.divider()

    if st.button("Generate Evaluation Report", type="primary"):

        final_user_id = None

        if selected_session != "None":
            for session in sessions:
                if session["label"] == selected_session:
                    final_user_id = session["user_id"]
                    break

        elif manual_user_id:
            final_user_id = manual_user_id

        if final_user_id:
            st.query_params["user_id"] = final_user_id
            st.rerun()
        else:
            st.error("Please select a session or enter a User ID")

    st.stop()

with st.spinner(
    "Fetching interview transcript..."
):

    conversation = get_interview_data(
        user_id
    )

if not conversation:

    st.title(
        "🎯 VIDYA Interview Evaluator"
    )

    st.error(
        f"No interview transcript found for user: {user_id}"
    )

    st.stop()

with st.spinner(
    "Generating evaluation..."
):

    report = evaluate_interview(
        conversation
    )

    mastery = calculate_mastery(
        report
    )

readiness_score = report.get(
    "readiness_score",
    0
)

rubric = report.get(
    "rubric_scores",
    {}
)

strengths = report.get(
    "strengths",
    []
)

gaps = report.get(
    "gaps",
    []
)

summary = report.get(
    "summary",
    "No summary available."
)

st.success(
    "Evaluation Generated Successfully"
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
        user_id
    )

    st.markdown(
        "#### Session"
    )

    st.info(
        "Latest Interview"
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

    row1 = st.columns(
        4
    )

    with row1[0]:

        st.metric(
            "Readiness",
            readiness_score
        )

    with row1[1]:

        st.metric(
            "Clarity",
            rubric.get(
                "clarity_structure",
                0
            )
        )

    with row1[2]:

        st.metric(
            "Technical",
            rubric.get(
                "technical_depth",
                0
            )
        )

    with row1[3]:

        st.metric(
            "Confidence",
            rubric.get(
                "confidence",
                0
            )
        )

    row2 = st.columns(
        3
    )

    with row2[0]:

        st.metric(
            "Storytelling",
            rubric.get(
                "storytelling",
                0
            )
        )

    with row2[1]:

        st.metric(
            "Question Handling",
            rubric.get(
                "question_handling",
                0
            )
        )

    with row2[2]:

        st.metric(
            "Mastery",
            f"{int(mastery * 100)}%"
        )

    st.divider()

    st.markdown(
        f"## Interview Transcript ({len(conversation)} Questions)"
    )

    transcript_container = st.container(
        border=True
    )

    with transcript_container:

        if len(conversation) == 0:

            st.warning(
                "Transcript is empty."
            )

        else:

            for index, item in enumerate(
                conversation,
                start=1
            ):

                question = item.get(
                    "question",
                    ""
                )

                answer = item.get(
                    "answer",
                    ""
                )

                st.markdown(
                    f"""
                    <div class='question-box'>
                    <b>Question {index}</b><br><br>
                    {question}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class='answer-box'>
                    <b>Answer</b><br><br>
                    {answer}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# =========================
# RIGHT PANEL
# =========================

with right_panel:

    st.markdown(
        "## Summary"
    )

    st.markdown(
        f"""
        <div class="summary-box">
        {summary}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        "## Strengths"
    )

    if strengths:

        for item in strengths:

            st.success(
                item
            )

    else:

        st.info(
            "No strengths identified."
        )

    st.divider()

    st.markdown(
        "## Learning Gaps"
    )

    if gaps:

        for item in gaps:

            st.warning(
                item
            )

    else:

        st.info(
            "No learning gaps identified."
        )
