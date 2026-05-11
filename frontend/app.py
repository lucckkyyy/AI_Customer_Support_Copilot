"""
Streamlit Dashboard — Customer Support Copilot
A clean ticket management UI for support agents.
"""
import streamlit as st
import httpx
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Support Copilot",
    page_icon="🎧",
    layout="wide",
)

# ── Helpers ───────────────────────────────────────────────────────────────────
def api_get(path: str):
    try:
        r = httpx.get(f"{API_BASE}{path}", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def api_post(path: str, data: dict):
    try:
        r = httpx.post(f"{API_BASE}{path}", json=data, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def api_put(path: str, data: dict):
    try:
        r = httpx.put(f"{API_BASE}{path}", json=data, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def status_badge(status: str) -> str:
    colors = {
        "open": "🔴 Open",
        "in_progress": "🟡 In Progress",
        "resolved": "🟢 Resolved",
    }
    return colors.get(status, status)


def priority_badge(priority: str) -> str:
    icons = {"low": "🔵", "medium": "🟠", "high": "🔺"}
    return f"{icons.get(priority, '')} {priority.capitalize()}"


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/headset.png", width=80)
st.sidebar.title("Support Copilot")
st.sidebar.markdown("*AI-powered ticket assistant*")
st.sidebar.divider()
page = st.sidebar.radio("Navigate", ["📋 Ticket Queue", "➕ New Ticket", "📊 Dashboard"])

# ── Page: Ticket Queue ────────────────────────────────────────────────────────
if page == "📋 Ticket Queue":
    st.title("📋 Ticket Queue")

    col1, col2 = st.columns([3, 1])
    with col2:
        status_filter = st.selectbox("Filter by status", ["All", "open", "in_progress", "resolved"])

    path = "/tickets/" if status_filter == "All" else f"/tickets/?status={status_filter}"
    tickets = api_get(path) or []

    if not tickets:
        st.info("No tickets found.")
    else:
        for ticket in tickets:
            with st.expander(
                f"#{ticket['id']} — {ticket['subject']} | "
                f"{status_badge(ticket['status'])} | {priority_badge(ticket['priority'])}",
                expanded=False,
            ):
                col_a, col_b = st.columns(2)
                col_a.markdown(f"**Customer ID:** `{ticket['customer_id']}`")
                col_b.markdown(f"**Email:** {ticket['customer_email']}")
                st.markdown(f"**Message:**\n> {ticket['body']}")

                if ticket.get("ai_response"):
                    st.markdown("---")
                    st.markdown("**🤖 AI Draft Response:**")
                    st.success(ticket["ai_response"])
                else:
                    st.warning("No AI response generated yet.")

                col1, col2, col3 = st.columns(3)

                # Generate AI response button
                with col1:
                    if st.button("🤖 Generate AI Response", key=f"gen_{ticket['id']}"):
                        with st.spinner("Agent is thinking... (may take 15-30s)"):
                            result = api_post(f"/tickets/{ticket['id']}/generate", {})
                            if result:
                                st.success("Response generated! Refresh to view.")
                                st.rerun()

                # Mark resolved
                with col2:
                    if ticket["status"] != "resolved":
                        if st.button("✅ Mark Resolved", key=f"res_{ticket['id']}"):
                            api_put(f"/tickets/{ticket['id']}/status", {"status": "resolved"})
                            st.rerun()

                # Mark in progress
                with col3:
                    if ticket["status"] == "open":
                        if st.button("▶️ Mark In Progress", key=f"prog_{ticket['id']}"):
                            api_put(f"/tickets/{ticket['id']}/status", {"status": "in_progress"})
                            st.rerun()


# ── Page: New Ticket ──────────────────────────────────────────────────────────
elif page == "➕ New Ticket":
    st.title("➕ Create New Ticket")

    # Load customers for dropdown
    customers = api_get("/customers/") or []
    customer_map = {f"{c['name']} ({c['id']})": c for c in customers}

    with st.form("new_ticket_form"):
        selected = st.selectbox("Customer", list(customer_map.keys()))
        subject = st.text_input("Subject", placeholder="e.g. Cannot login to my account")
        body = st.text_area("Customer Message", height=150, placeholder="Paste the customer's message here...")
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
        submitted = st.form_submit_button("Create Ticket")

    if submitted:
        if not subject or not body:
            st.error("Subject and message are required.")
        else:
            customer = customer_map[selected]
            result = api_post("/tickets/", {
                "customer_id": customer["id"],
                "customer_email": customer["email"],
                "subject": subject,
                "body": body,
                "priority": priority,
            })
            if result:
                st.success(f"✅ Ticket #{result['id']} created successfully!")
                st.info("Go to 'Ticket Queue' to generate an AI response.")


# ── Page: Dashboard ───────────────────────────────────────────────────────────
elif page == "📊 Dashboard":
    st.title("📊 Overview Dashboard")

    tickets = api_get("/tickets/") or []

    total = len(tickets)
    open_t = sum(1 for t in tickets if t["status"] == "open")
    in_prog = sum(1 for t in tickets if t["status"] == "in_progress")
    resolved = sum(1 for t in tickets if t["status"] == "resolved")
    ai_generated = sum(1 for t in tickets if t.get("ai_response"))

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Tickets", total)
    col2.metric("🔴 Open", open_t)
    col3.metric("🟡 In Progress", in_prog)
    col4.metric("🟢 Resolved", resolved)
    col5.metric("🤖 AI Responses", ai_generated)

    st.divider()
    st.subheader("Recent Tickets")

    for ticket in tickets[:10]:
        st.markdown(
            f"**#{ticket['id']}** — {ticket['subject']} | "
            f"{status_badge(ticket['status'])} | {priority_badge(ticket['priority'])}"
        )
