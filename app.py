import streamlit as st

from services.pinecone_service import get_interview_data
from services.evaluator import evaluate_interview
from services.mastery import calculate_mastery

st.set_page_config(
    page_title="VIDYA Interview Evaluator",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 VIDYA Interview Evaluator")

st.markdown(
    "Evaluate completed interview sessions stored in Pinecone."
)

user_options = [
    "user_001 - Beginner AI Student",
    "user_002 - ML Engineer",
    "user_003 - GenAI Engineer",
    "user_004 - AI Architect",
    "user_005 - Weak Candidate"
]

selected_user = st.selectbox(
    "Select User",
    user_options
)

user_id = selected_user.split(" - ")[0]

if st.button("Evaluate Interview"):

    with st.spinner("Fetching interview data..."):

        conversation = get_interview_data(
            user_id
        )

    if not conversation:

        st.error(
            f"No interview responses found for user: {user_id}"
        )

    else:

        with st.spinner("Generating evaluation..."):

            report = evaluate_interview(
                conversation
            )

            mastery = calculate_mastery(
                report
            )

        st.success(
            "Evaluation Generated Successfully"
        )

        st.subheader(
            "Backend Response"
        )

        st.json(
            report
        )

        st.divider()

        st.subheader(
            "Evaluation Metrics"
        )

        readiness = report.get(
            "readiness_score",
            0
        )

        rubric = report.get(
            "rubric_scores",
            {}
        )

        st.metric(
            "Interview Readiness",
            readiness
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Clarity & Structure",
                rubric.get(
                    "clarity_structure",
                    0
                )
            )

        with col2:

            st.metric(
                "Technical Depth",
                rubric.get(
                    "technical_depth",
                    0
                )
            )

        with col3:

            st.metric(
                "Confidence",
                rubric.get(
                    "confidence",
                    0
                )
            )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Storytelling",
                rubric.get(
                    "storytelling",
                    0
                )
            )

        with col2:

            st.metric(
                "Question Handling",
                rubric.get(
                    "question_handling",
                    0
                )
            )

        st.metric(
            "Mastery",
            mastery
        )

        st.divider()

        st.subheader(
            "Strengths"
        )

        strengths = report.get(
            "strengths",
            []
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

        st.subheader(
            "Learning Gaps"
        )

        gaps = report.get(
            "gaps",
            []
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

        st.subheader(
            "Summary"
        )

        st.write(
            report.get(
                "summary",
                "No summary available."
            )
        )

        with st.expander(
            "Interview Transcript"
        ):

            st.json(
                conversation
            )