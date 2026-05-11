"""
Knowledge Base — ChromaDB vector store for support documentation.
Documents are embedded and stored locally; retrieved at query time via semantic search.
"""
import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = "support_knowledge_base"

# ── Hardcoded support docs (add your own or load from files) ──────────────────
SUPPORT_DOCS = [
    {
        "id": "kb-001",
        "content": "To reset your password, go to Settings > Security > Reset Password. You will receive a reset link at your registered email address within 5 minutes.",
        "metadata": {"category": "account", "topic": "password_reset"},
    },
    {
        "id": "kb-002",
        "content": "To upgrade your plan from Free to Pro, navigate to Settings > Billing > Upgrade Plan. Pro includes unlimited API calls, priority support, and advanced analytics.",
        "metadata": {"category": "billing", "topic": "upgrade"},
    },
    {
        "id": "kb-003",
        "content": "Refund Policy: We offer a 30-day money-back guarantee for all paid plans. To request a refund, contact support with your invoice number. Refunds are processed within 5-7 business days.",
        "metadata": {"category": "billing", "topic": "refund"},
    },
    {
        "id": "kb-004",
        "content": "API rate limits: Free plan — 100 requests/day. Pro plan — 10,000 requests/day. Enterprise plan — unlimited. Rate limit errors return HTTP 429.",
        "metadata": {"category": "api", "topic": "rate_limits"},
    },
    {
        "id": "kb-005",
        "content": "To integrate our API, generate an API key from Settings > API Keys. Include it in the Authorization header: 'Authorization: Bearer YOUR_API_KEY'. Full API docs at docs.ourapp.com.",
        "metadata": {"category": "api", "topic": "integration"},
    },
    {
        "id": "kb-006",
        "content": "Data export: You can export all your data in CSV or JSON format from Settings > Data > Export. Enterprise customers can also use our bulk export API.",
        "metadata": {"category": "data", "topic": "export"},
    },
    {
        "id": "kb-007",
        "content": "Two-factor authentication (2FA): Enable 2FA from Settings > Security > Two-Factor Auth. We support Google Authenticator, Authy, and SMS-based 2FA.",
        "metadata": {"category": "account", "topic": "2fa"},
    },
    {
        "id": "kb-008",
        "content": "If you cannot log in, check that Caps Lock is off and you're using the correct email. After 5 failed attempts your account is locked for 15 minutes. Contact support if the issue persists.",
        "metadata": {"category": "account", "topic": "login_issues"},
    },
    {
        "id": "kb-009",
        "content": "To cancel your subscription, go to Settings > Billing > Cancel Subscription. Your access continues until the end of the current billing period. No partial refunds for early cancellation.",
        "metadata": {"category": "billing", "topic": "cancellation"},
    },
    {
        "id": "kb-010",
        "content": "Enterprise SLA: Response time within 4 hours for critical issues, 24 hours for standard issues. A dedicated account manager is assigned to all enterprise customers.",
        "metadata": {"category": "support", "topic": "enterprise_sla"},
    },
]


def _get_collection():
    """Initialise ChromaDB client and return the knowledge base collection."""
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    ef = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def seed_knowledge_base() -> None:
    """
    Idempotently seed support docs into ChromaDB.
    Skips docs that already exist (checked by ID).
    """
    collection = _get_collection()
    existing_ids = set(collection.get()["ids"])

    new_docs = [d for d in SUPPORT_DOCS if d["id"] not in existing_ids]
    if not new_docs:
        print("✅ Knowledge base already seeded.")
        return

    collection.add(
        ids=[d["id"] for d in new_docs],
        documents=[d["content"] for d in new_docs],
        metadatas=[d["metadata"] for d in new_docs],
    )
    print(f"✅ Seeded {len(new_docs)} documents into knowledge base.")


def retrieve_knowledge(query: str, n_results: int = 3) -> str:
    """
    Semantic search over the knowledge base.
    Returns the top-n most relevant support documents as a formatted string.
    """
    collection = _get_collection()
    results = collection.query(query_texts=[query], n_results=n_results)

    docs = results.get("documents", [[]])[0]
    if not docs:
        return "No relevant knowledge base articles found."

    formatted = "\n\n".join(
        f"[KB Article {i+1}]: {doc}" for i, doc in enumerate(docs)
    )
    return f"Relevant knowledge base articles:\n\n{formatted}"
