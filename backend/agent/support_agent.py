"""
Support Agent — the brain of the copilot.

Flow for each ticket:
  1. Retrieve customer memories from Mem0
  2. Fetch relevant KB articles via RAG
  3. Run LangChain agent with CRM + billing tools
  4. Store the interaction back to Mem0
  5. Return the ready-to-review AI response
"""
import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

from tools.crm_tool import get_customer_crm_info
from tools.billing_tool import get_billing_info
from rag.knowledge_base import retrieve_knowledge
from memory.mem0_client import add_memory, get_memories

load_dotenv()

# ── Tools available to the agent ─────────────────────────────────────────────
TOOLS = [get_customer_crm_info, get_billing_info]

# ── Prompt ────────────────────────────────────────────────────────────────────
SYSTEM_TEMPLATE = """You are an expert AI Customer Support Copilot for a SaaS company.
Your job is to help support agents by drafting thorough, empathetic, and accurate responses to customer tickets.

You have access to:
- CRM tool: fetch customer profile, plan, and account manager info
- Billing tool: fetch payment history, subscription details, and invoice info
- Knowledge base context: relevant support articles (provided below)
- Customer memory: facts from previous interactions (provided below)

Guidelines:
- Always greet the customer by name (look up their name via CRM first).
- Be empathetic and professional.
- Use knowledge base articles to ground your answer in facts.
- Reference prior interactions from memory when relevant.
- For billing disputes, always fetch billing info before responding.
- End with a clear next step or call to action.
- Draft the response as if a human support agent will review and send it.

---
{kb_context}

---
{memory_context}
---
"""

def build_agent() -> AgentExecutor:
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.3,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_TEMPLATE),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(llm, TOOLS, prompt)
    return AgentExecutor(agent=agent, tools=TOOLS, verbose=True, max_iterations=5)


def generate_response(
    customer_id: str,
    ticket_subject: str,
    ticket_body: str,
) -> str:
    """
    Main entry point — generates a draft support response for a given ticket.

    Args:
        customer_id:    e.g. "CUST-001"
        ticket_subject: e.g. "Cannot login to my account"
        ticket_body:    The full message from the customer

    Returns:
        A draft response string ready for agent review.
    """
    # 1. Retrieve relevant KB articles
    query = f"{ticket_subject} {ticket_body}"
    kb_context = retrieve_knowledge(query)

    # 2. Retrieve customer memories from Mem0
    memory_context = get_memories(customer_id) or "No previous interactions on record."

    # 3. Build and run the agent
    agent_executor = build_agent()

    user_input = (
        f"Customer ID: {customer_id}\n"
        f"Ticket Subject: {ticket_subject}\n"
        f"Customer Message:\n{ticket_body}\n\n"
        f"Please draft a complete, professional response to this support ticket. "
        f"Start by looking up the customer's CRM profile. "
        f"If the issue is billing-related, also fetch billing info."
    )

    result = agent_executor.invoke({
        "input": user_input,
        "kb_context": kb_context,
        "memory_context": memory_context,
    })

    ai_response = result.get("output", "Unable to generate a response.")

    # 4. Save interaction to Mem0 for future context
    add_memory(customer_id, [
        {"role": "user",      "content": f"[{ticket_subject}] {ticket_body}"},
        {"role": "assistant", "content": ai_response},
    ])

    return ai_response
