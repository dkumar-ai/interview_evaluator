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

payload_user_001 = {
    "responses": [
        {
            "question_id": "q_001",
            "question": "What is the difference between AI, ML and Deep Learning? Use a real-world product as your example.",
            "answer": "AI is the broader field of building systems that perform tasks requiring intelligence. Machine Learning is a subset where systems learn from data. Deep Learning uses neural networks with multiple layers. For example, Netflix recommendations use ML models while modern content understanding and personalization increasingly use deep learning techniques."
        },
        {
            "question_id": "q_002",
            "question": "What is overfitting and how have you seen it cause a real project to fail?",
            "answer": "Overfitting happens when a model memorizes training data instead of learning patterns. During a student project, a churn model achieved very high training accuracy but failed on new customer data because it had learned noise rather than meaningful signals."
        },
        {
            "question_id": "q_003",
            "question": "Explain bias vs variance — not the definition, but when it actually matters in practice.",
            "answer": "It matters when deciding whether a model is too simple or too complex. In a prediction project, increasing model complexity improved training accuracy but validation performance dropped, showing variance was becoming a bigger problem than bias."
        },
        {
            "question_id": "q_004",
            "question": "What is the difference between supervised and unsupervised learning? Give one example of each from daily life.",
            "answer": "Supervised learning uses labeled examples such as spam email detection. Unsupervised learning finds patterns without labels, such as grouping customers based on purchasing behavior for marketing campaigns."
        },
        {
            "question_id": "q_005",
            "question": "You trained a model and accuracy is 95%. Is that good?",
            "answer": "Not necessarily. I would first check class balance, precision, recall and business impact. A fraud detection model with 95% accuracy could still be useless if it misses most fraud cases."
        },
        {
            "question_id": "q_006",
            "question": "What is a neural network and how does it learn?",
            "answer": "A neural network consists of layers of connected neurons. During training, weights are adjusted using backpropagation and gradient descent to reduce prediction error and improve performance."
        },
        {
            "question_id": "q_007",
            "question": "What does a confusion matrix tell you and when would you use precision vs recall?",
            "answer": "A confusion matrix shows correct and incorrect predictions. Precision is important when false positives are costly, while recall matters when missing positive cases would create larger business risks."
        },
        {
            "question_id": "q_008",
            "question": "What is cross-validation and why do we bother with it?",
            "answer": "Cross-validation repeatedly splits data into training and validation sets. It provides a more reliable estimate of model performance and helps reduce the risk of overfitting to a single split."
        },
        {
            "question_id": "q_009",
            "question": "What is a large language model and how is it different from a search engine?",
            "answer": "An LLM generates responses based on learned patterns from training data. A search engine retrieves existing information from indexed documents. LLMs generate language while search engines primarily retrieve information."
        },
        {
            "question_id": "q_010",
            "question": "What is prompt engineering? Show a bad prompt and how you would improve it.",
            "answer": "Prompt engineering involves designing instructions that guide model behavior. Instead of asking 'Explain AI', I would ask 'Explain AI to a college student using real-world examples and keep it under 200 words.'"
        }
    ]
}

payload_user_002 = {
    "responses": [
        {
            "question_id": "q_001",
            "question": "Walk me through your MLOps setup. How do you handle model drift in production?",
            "answer": "I use automated pipelines for training, validation and deployment. Model performance metrics are continuously monitored. When drift indicators exceed thresholds, retraining is triggered using fresh production data after validation checks."
        },
        {
            "question_id": "q_002",
            "question": "How do you evaluate a model when your labels are noisy or partially missing?",
            "answer": "I validate label quality through sampling, use robust evaluation metrics and sometimes create a manually verified benchmark dataset to estimate true model performance."
        },
        {
            "question_id": "q_003",
            "question": "Your model performs great offline but degrades after two weeks in production. Debug this.",
            "answer": "I would investigate data drift, feature pipeline changes, seasonality effects and production input distributions. Monitoring dashboards and historical comparisons help identify the root cause."
        },
        {
            "question_id": "q_004",
            "question": "Explain feature stores. What problem do they solve?",
            "answer": "Feature stores centralize feature definitions and ensure consistency between training and serving environments. They reduce duplication and prevent training-serving skew."
        },
        {
            "question_id": "q_005",
            "question": "How do you decide between retraining from scratch and fine-tuning?",
            "answer": "If the new data significantly changes the problem space, retraining is preferred. Fine-tuning is useful when the core patterns remain similar and only incremental adaptation is needed."
        },
        {
            "question_id": "q_006",
            "question": "Walk me through building a training pipeline for a ranking model.",
            "answer": "I would start with data collection, feature generation, dataset versioning, offline evaluation, hyperparameter tuning and automated deployment through CI/CD pipelines."
        },
        {
            "question_id": "q_007",
            "question": "What is data leakage? Give a non-obvious example.",
            "answer": "Data leakage occurs when future information unintentionally influences training. For example, including post-purchase activity when predicting future purchases creates unrealistic performance."
        },
        {
            "question_id": "q_008",
            "question": "What is the difference between fine-tuning and RAG?",
            "answer": "Fine-tuning updates model weights while RAG retrieves external information during inference. I would use RAG for frequently changing knowledge and fine-tuning for behavior customization."
        },
        {
            "question_id": "q_009",
            "question": "What is LoRA and why is it preferred?",
            "answer": "LoRA updates a small subset of parameters instead of the full model. It significantly reduces training cost, memory requirements and deployment complexity."
        },
        {
            "question_id": "q_010",
            "question": "How do you reduce hallucinations in a production LLM system?",
            "answer": "I use RAG pipelines, trusted knowledge sources, response validation, prompt constraints and human feedback loops to improve factual accuracy."
        }
    ]
}

payload_user_003 = {
    "responses": [
        {
            "question_id": "q_001",
            "question": "Explain the transformer attention mechanism. Why does self-attention scale quadratically and how do people work around it?",
            "answer": "Self-attention allows each token to compare itself with every other token in the sequence. This creates an N×N attention matrix, causing memory and computation costs to grow quadratically with sequence length. Modern approaches such as FlashAttention, sparse attention and grouped query attention help reduce these costs while maintaining model quality."
        },
        {
            "question_id": "q_002",
            "question": "What is the difference between encoder-only, decoder-only and encoder-decoder architectures?",
            "answer": "Encoder-only models like BERT are optimized for understanding tasks. Decoder-only models like GPT are optimized for text generation. Encoder-decoder architectures like T5 combine both and work well for translation, summarization and sequence transformation tasks."
        },
        {
            "question_id": "q_003",
            "question": "What is tokenization and how does a poor tokenizer hurt domain-specific applications?",
            "answer": "Tokenization converts text into smaller units that models can process. Poor tokenization can split technical or domain-specific terms inefficiently, increasing token count and reducing semantic understanding in areas such as medicine or law."
        },
        {
            "question_id": "q_004",
            "question": "Explain temperature and top-p. How would you tune them for customer support versus creative writing?",
            "answer": "Temperature controls randomness while top-p controls the probability mass considered during generation. For customer support I would use lower temperature values for consistency and accuracy. For creative writing I would increase temperature and top-p to encourage more diverse outputs."
        },
        {
            "question_id": "q_005",
            "question": "What are scaling laws and why do they matter?",
            "answer": "Scaling laws describe how model performance improves with additional parameters, data and compute. They help teams estimate whether investing in larger models will provide enough value to justify the additional infrastructure cost."
        },
        {
            "question_id": "q_006",
            "question": "Design a RAG-based customer support chatbot.",
            "answer": "I would ingest support documents, chunk them appropriately, generate embeddings and store them in Pinecone. Retrieval would use hybrid search and reranking. Retrieved context would be sent to the LLM along with conversation history. Monitoring and feedback collection would be used to improve quality."
        },
        {
            "question_id": "q_007",
            "question": "How do you evaluate retrieval quality in a RAG system?",
            "answer": "I use metrics such as Recall@K, Precision@K and Mean Reciprocal Rank. I also maintain a golden dataset containing representative user queries and expected supporting documents."
        },
        {
            "question_id": "q_008",
            "question": "What is the difference between standard RAG and Graph RAG?",
            "answer": "Standard RAG retrieves documents based on semantic similarity. Graph RAG uses entity relationships stored in a graph structure, making it useful for complex knowledge domains where relationships between entities are important."
        },
        {
            "question_id": "q_009",
            "question": "How do you handle long documents that exceed the context window?",
            "answer": "I use hierarchical chunking, summarization and retrieval strategies. Relevant sections are selected dynamically instead of sending entire documents to the model."
        },
        {
            "question_id": "q_010",
            "question": "What is the difference between an LLM chain and a true AI agent?",
            "answer": "An LLM chain follows predefined steps while an agent can make decisions, choose tools and adapt its workflow based on goals and intermediate results. Agentic systems provide more flexibility but introduce additional complexity."
        }
    ]
}

payload_user_004 = {
    "responses": [
        {
            "question_id": "q_001",
            "question": "Design an LLM-powered document search and Q&A system for 10M enterprise documents.",
            "answer": "I would build separate ingestion, indexing, retrieval and serving layers. Documents would be processed asynchronously, embedded and stored in a vector database. Hybrid retrieval and reranking would improve quality. Responses would be generated through a controlled RAG pipeline with observability and governance built in."
        },
        {
            "question_id": "q_002",
            "question": "Design a real-time personalization system for 500M users.",
            "answer": "The architecture would combine streaming pipelines, feature stores and low-latency serving layers. User behavior events would update recommendation signals continuously while online ranking models personalize results in real time."
        },
        {
            "question_id": "q_003",
            "question": "Design a multi-agent orchestration system for autonomous code review.",
            "answer": "I would separate planning, analysis and validation agents. A central orchestrator would manage workflow execution, retries and escalation. Validation agents would verify outputs before recommendations reach developers."
        },
        {
            "question_id": "q_004",
            "question": "You need p99 inference latency below 200ms. What optimizations would you apply?",
            "answer": "I would use quantized models, KV caching, optimized serving frameworks, batching and model routing. Caching common responses and reducing token generation length can significantly improve latency."
        },
        {
            "question_id": "q_005",
            "question": "How do you architect a shared GenAI platform for multiple teams?",
            "answer": "I would provide centralized infrastructure, model gateways, monitoring and governance while allowing teams to customize prompts, workflows and retrieval systems independently."
        },
        {
            "question_id": "q_006",
            "question": "Why is LLM inference often memory-bound instead of compute-bound?",
            "answer": "Inference frequently spends more time moving model weights through memory than performing calculations. Memory bandwidth therefore becomes a major bottleneck for large models."
        },
        {
            "question_id": "q_007",
            "question": "What is FlashAttention?",
            "answer": "FlashAttention optimizes memory access patterns during attention computation. It reduces memory usage and improves throughput while producing equivalent outputs."
        },
        {
            "question_id": "q_008",
            "question": "Compare RLHF, DPO and PPO.",
            "answer": "RLHF uses human preferences with reinforcement learning. PPO is a popular optimization algorithm used within RLHF pipelines. DPO simplifies alignment by directly optimizing preference data without requiring reinforcement learning infrastructure."
        },
        {
            "question_id": "q_009",
            "question": "What is quantization and where does it break down?",
            "answer": "Quantization reduces model precision to lower memory and compute costs. Aggressive quantization can hurt accuracy, especially for sensitive reasoning or mathematical tasks."
        },
        {
            "question_id": "q_010",
            "question": "Build versus buy for vector databases. When would you choose Pinecone?",
            "answer": "I would choose Pinecone when operational simplicity, scalability and managed infrastructure are priorities. Self-hosted alternatives make sense when organizations require complete infrastructure control."
        }
    ]
}

payload_user_005 = {
    "responses": [
        {
            "question_id": "q_001",
            "question": "You said you built a RAG system. Walk me through exactly how you chose your chunk size and why.",
            "answer": "I mostly used the default chunk size from the framework. I experimented with a few values but did not formally evaluate retrieval quality. I mainly focused on getting the application working."
        },
        {
            "question_id": "q_002",
            "question": "You listed fine-tuning on your resume. What was your loss curve doing on epoch 3?",
            "answer": "I don't remember the exact numbers. I monitored training loss and validation accuracy but I did not analyze the curves in much detail."
        },
        {
            "question_id": "q_003",
            "question": "You said the model performed well. What were the actual metrics and baseline?",
            "answer": "The accuracy improved compared to the initial version. I don't remember the exact metrics or baseline values because I was not responsible for tracking them."
        },
        {
            "question_id": "q_004",
            "question": "Explain the transformer attention mechanism without giving the formula.",
            "answer": "Attention helps the model understand which words are important. It looks at different parts of the text and uses that information to generate better responses."
        },
        {
            "question_id": "q_005",
            "question": "You said you used LangChain. What is it doing under the hood?",
            "answer": "LangChain helps connect language models with tools and prompts. I mainly used existing components and did not spend much time understanding the internal implementation."
        },
        {
            "question_id": "q_006",
            "question": "Tell me about deploying AI systems to production.",
            "answer": "Most of my work has been in notebooks and local environments. I have limited experience deploying AI systems into production."
        },
        {
            "question_id": "q_007",
            "question": "Give me a real example from your work where AI created business value.",
            "answer": "I worked on a chatbot project that answered user questions. It worked reasonably well but I was not involved in measuring business impact."
        },
        {
            "question_id": "q_008",
            "question": "How do you evaluate a RAG pipeline?",
            "answer": "I usually check whether the answers look correct. I know there are evaluation metrics available but I have not used them extensively."
        },
        {
            "question_id": "q_009",
            "question": "Name the trade-offs between Pinecone, Weaviate and pgvector.",
            "answer": "I know they are vector databases but I have not done a detailed comparison between them."
        },
        {
            "question_id": "q_010",
            "question": "Why should we hire you for a GenAI role?",
            "answer": "I am eager to learn, interested in AI and willing to improve my technical skills. While I lack deep production experience, I am motivated to grow quickly."
        }
    ]
}

users = {
    "user_001": payload_user_001,   # Beginner AI Student
    "user_002": payload_user_002,   # ML Engineer
    "user_003": payload_user_003,   # GenAI Engineer
    "user_004": payload_user_004,   # AI Architect
    "user_005": payload_user_005    # Weak Candidate
}

vector = [0.001] * dimension

for user_id, payload in users.items():

    index.upsert(
        vectors=[
            {
                "id": f"{user_id}_interview_responses",
                "values": vector,
                "metadata": {
                    "doc_type": "interview_responses",
                    "user_id": user_id,
                    "session_id": f"{user_id}_session",
                    "module_id": "mod_genai_001",
                    "timestamp": 1780401000,
                    "text": json.dumps(payload)
                }
            }
        ],
        namespace=user_id
    )

    print(f"✅ Inserted {user_id}")

print("\n🎉 All 5 users inserted successfully")