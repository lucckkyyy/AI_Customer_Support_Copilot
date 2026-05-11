"""
CRM Tool — simulates a real CRM lookup.
In production you'd swap the dict for a real CRM API call (Salesforce, HubSpot, etc.)
"""
from langchain.tools import tool

# ---------- Simulated CRM data ----------
MOCK_CRM: dict[str, dict] = {
    "CUST-001": {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "plan": "pro",
        "account_status": "active",
        "tickets_opened": 3,
        "account_manager": "Sarah Lee",
        "notes": "High-value customer; prefers email communication.",
    },
    "CUST-002": {
        "name": "Bob Smith",
        "email": "bob@example.com",
        "plan": "enterprise",
        "account_status": "active",
        "tickets_opened": 12,
        "account_manager": "David Kim",
        "notes": "Enterprise client — SLA: 4-hour response time.",
    },
    "CUST-003": {
        "name": "Carol Williams",
        "email": "carol@example.com",
        "plan": "free",
        "account_status": "active",
        "tickets_opened": 1,
        "account_manager": None,
        "notes": "New user; onboarding not completed.",
    },
}


@tool
def get_customer_crm_info(customer_id: str) -> str:
    """
    Fetches CRM profile for a customer by their customer ID.
    Returns account details, plan type, account manager, and any notes.
    Use this when you need context about who the customer is.
    """
    data = MOCK_CRM.get(customer_id.upper())
    if not data:
        return f"No CRM record found for customer ID: {customer_id}"

    return (
        f"CRM Record for {customer_id}:\n"
        f"  Name           : {data['name']}\n"
        f"  Email          : {data['email']}\n"
        f"  Plan           : {data['plan']}\n"
        f"  Account Status : {data['account_status']}\n"
        f"  Tickets Opened : {data['tickets_opened']}\n"
        f"  Account Manager: {data['account_manager'] or 'N/A'}\n"
        f"  Notes          : {data['notes']}"
    )
