import json
import os
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
        top_k=50,
        include_metadata=True
    )

    conversation = []

    for match in results.matches:

        if match.metadata.get("doc_type") != "interview_responses":
            continue

        data = json.loads(
            match.metadata.get("text", "{}")
        )

        for response in data.get("responses", []):

            conversation.append(
                {
                    "question": response["question"],
                    "answer": response["answer"]
                }
            )

    return conversation