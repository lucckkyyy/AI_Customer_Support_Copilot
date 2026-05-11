"""
Billing Tool — simulates a billing/payment system lookup.
In production swap the dict for Stripe, Chargebee, etc.
"""
from langchain.tools import tool

MOCK_BILLING: dict[str, dict] = {
    "CUST-001": {
        "plan": "pro",
        "monthly_cost": 49.00,
        "billing_cycle": "monthly",
        "next_billing_date": "2026-06-01",
        "last_payment_status": "paid",
        "last_payment_amount": 49.00,
        "payment_method": "Visa ending in 4242",
        "invoices": ["INV-2024-001", "INV-2024-002"],
        "overdue": False,
    },
    "CUST-002": {
        "plan": "enterprise",
        "monthly_cost": 499.00,
        "billing_cycle": "annual",
        "next_billing_date": "2027-01-01",
        "last_payment_status": "paid",
        "last_payment_amount": 5988.00,
        "payment_method": "ACH Bank Transfer",
        "invoices": ["INV-2024-ENT-001"],
        "overdue": False,
    },
    "CUST-003": {
        "plan": "free",
        "monthly_cost": 0.00,
        "billing_cycle": "N/A",
        "next_billing_date": "N/A",
        "last_payment_status": "N/A",
        "last_payment_amount": 0.00,
        "payment_method": "N/A",
        "invoices": [],
        "overdue": False,
    },
}


@tool
def get_billing_info(customer_id: str) -> str:
    """
    Fetches billing and payment information for a customer by their customer ID.
    Returns plan cost, billing cycle, payment status, and invoice history.
    Use this when the customer's issue involves payments, charges, or subscription questions.
    """
    data = MOCK_BILLING.get(customer_id.upper())
    if not data:
        return f"No billing record found for customer ID: {customer_id}"

    overdue_flag = "⚠️ OVERDUE" if data["overdue"] else "✅ Current"
    return (
        f"Billing Record for {customer_id}:\n"
        f"  Plan               : {data['plan']}\n"
        f"  Monthly Cost       : ${data['monthly_cost']:.2f}\n"
        f"  Billing Cycle      : {data['billing_cycle']}\n"
        f"  Next Billing Date  : {data['next_billing_date']}\n"
        f"  Last Payment Status: {data['last_payment_status']} {overdue_flag}\n"
        f"  Last Payment Amount: ${data['last_payment_amount']:.2f}\n"
        f"  Payment Method     : {data['payment_method']}\n"
        f"  Invoices           : {', '.join(data['invoices']) or 'None'}"
    )
