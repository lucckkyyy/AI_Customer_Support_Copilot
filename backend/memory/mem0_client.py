"""
Mem0 Client — handles persistent customer memory across sessions.
Mem0 stores and retrieves facts about customers automatically,
so the agent always has context about previous interactions.
"""
import os
from mem0 import MemoryClient
from dotenv import load_dotenv

load_dotenv()

# Initialise once — reused across all requests
_client: MemoryClient | None = None


def get_mem0_client() -> MemoryClient:
    global _client
    if _client is None:
        _client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
    return _client


def add_memory(customer_id: str, messages: list[dict]) -> None:
    """
    Persist a conversation turn to Mem0.
    messages: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    """
    client = get_mem0_client()
    client.add(messages, user_id=customer_id)


def get_memories(customer_id: str) -> str:
    """
    Retrieve all stored memories for a customer as a formatted string.
    Returns empty string if no memories exist yet.
    """
    client = get_mem0_client()
    memories = client.get_all(user_id=customer_id)

    if not memories:
        return ""

    facts = [m.get("memory", "") for m in memories if m.get("memory")]
    if not facts:
        return ""

    formatted = "\n".join(f"  - {fact}" for fact in facts)
    return f"Known facts about this customer from past interactions:\n{formatted}"


def search_memories(customer_id: str, query: str) -> str:
    """
    Search memories relevant to a specific query for a customer.
    Useful for targeted recall (e.g., 'did they report a billing issue before?')
    """
    client = get_mem0_client()
    results = client.search(query, user_id=customer_id)

    if not results:
        return "No relevant past interactions found."

    facts = [r.get("memory", "") for r in results if r.get("memory")]
    return "\n".join(f"  - {fact}" for fact in facts) or "No relevant memories found."
