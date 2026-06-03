import json
import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

index_name = os.getenv("PINECONE_INDEX_NAME")

index = pc.Index(index_name)

try:
    stats = index.describe_index_stats()

    dimension = (
        stats.get("dimension")
        or stats.get("index_fullness")
        or 3072
    )

except Exception:
    dimension = 3072

print(f"Using dimension: {dimension}")

user_id = "test_user_001"

payload = {
    "responses": [
        {
            "question_id": "q_001",
            "question": "What is Python?",
            "answer": "Python is a high level programming language used for web development, AI, automation and backend services."
        },
        {
            "question_id": "q_002",
            "question": "Difference between List and Tuple?",
            "answer": "Lists are mutable while tuples are immutable. Lists are used when data changes frequently whereas tuples are useful for fixed collections."
        },
        {
            "question_id": "q_003",
            "question": "How would you design a REST API?",
            "answer": "I would create CRUD endpoints, add authentication using JWT, implement request validation, proper status codes, logging and error handling."
        }
    ]
}

vector = [0.001] * dimension

index.upsert(
    vectors=[
        {
            "id": f"{user_id}_interview_responses",
            "values": vector,
            "metadata": {
                "doc_type": "interview_responses",
                "user_id": user_id,
                "session_id": "test_sess_001",
                "module_id": "mod_python_backend_001",
                "timestamp": 1780401000,
                "text": json.dumps(payload)
            }
        }
    ],
    namespace=user_id
)

print("✅ Dummy interview inserted successfully")