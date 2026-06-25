import os
import json
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

index = pc.Index(
    os.getenv("PINECONE_INDEX_NAME")
)


def store_evaluation_result(
    user_id,
    session_id,
    report: dict
):

    user_id = str(user_id)
    session_id = str(session_id)

    vector_id = f"evaluation-{session_id}"

    index.upsert(
        vectors=[
            {
                "id": vector_id,
                "values": [0.001] * 3072,
                "metadata": {
                    "doc_type": "interview_evaluation",
                    "session_id": session_id,
                    "text": json.dumps(report)
                }
            }
        ],
        namespace=user_id
    )

    print(
        f"[PINECONE] Stored evaluation for "
        f"user={user_id} session={session_id}"
    )


def get_interview_data(user_id):

    user_id = str(user_id)

    results = index.query(
        namespace=user_id,
        vector=[0.001] * 3072,
        top_k=100,
        include_metadata=True
    )

    for match in results.matches:

        metadata = match.metadata

        if metadata.get("doc_type") != "interview_questions":
            continue

        text = metadata.get("text", "")

        try:

            parsed = json.loads(text)

            questions = parsed.get(
                "questions",
                []
            )

            conversation = []

            for item in questions:

                conversation.append(
                    {
                        "question": item.get(
                            "question",
                            item.get(
                                "text",
                                ""
                            )
                        ),
                        "answer": item.get(
                            "answer",
                            ""
                        )
                    }
                )

            return conversation

        except Exception as e:

            print(
                "PINECONE PARSE ERROR:",
                str(e)
            )

    return []


def get_evaluation_result(user_id, session_id):

    user_id = str(user_id)
    session_id = str(session_id)

    results = index.query(
        namespace=user_id,
        vector=[0.001] * 3072,
        top_k=100,
        include_metadata=True
    )

    # Check for completed evaluation
    for match in results.matches:

        metadata = match.metadata

        if (
            metadata.get("doc_type") == "interview_evaluation"
            and str(metadata.get("session_id")) == session_id
        ):

            try:
                return {
                    "status": "completed",
                    "report": json.loads(
                        metadata.get("text", "{}")
                    )
                }

            except Exception as e:

                print(
                    "EVALUATION PARSE ERROR:",
                    str(e)
                )

                return None

    # Check processing status
    for match in results.matches:

        metadata = match.metadata

        if (
            metadata.get("doc_type") == "evaluation_status"
            and str(metadata.get("session_id")) == session_id
        ):

            return {
                "status": metadata.get(
                    "status",
                    "PROCESSING"
                ),
                "report": None
            }

    return None


def get_all_sessions():

    results = index.query(
        vector=[0.001] * 3072,
        top_k=1000,
        include_metadata=True
    )

    sessions = []

    for match in results.matches:

        metadata = match.metadata

        if metadata.get("doc_type") == "interview_questions":

            user_id = str(match.namespace)

            session_id = str(
                metadata.get(
                    "session_id",
                    "Latest"
                )
            )

            session_label = (
                f"{user_id} - {session_id}"
            )

            sessions.append(
                {
                    "label": session_label,
                    "user_id": user_id,
                    "session_id": session_id
                }
            )

    return sessions
