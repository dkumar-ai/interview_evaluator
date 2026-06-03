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


def get_interview_data(user_id):

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