"""
FastAPI Backend — Customer Support Copilot
Endpoints:
  POST /tickets/           — Create a new support ticket
  GET  /tickets/           — List all tickets
  GET  /tickets/{id}       — Get a specific ticket
  POST /tickets/{id}/generate  — Run AI to generate response
  PUT  /tickets/{id}/status    — Update ticket status
  GET  /customers/         — List all customers
  GET  /health             — Health check
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import Optional
from contextlib import asynccontextmanager
import logging

from database.db import get_db, init_db
from database.models import Ticket, Customer, TicketStatus, TicketPriority
from rag.knowledge_base import seed_knowledge_base
from agent.support_agent import generate_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting up — initialising DB and knowledge base...")
    await init_db()
    seed_knowledge_base()
    logger.info("✅ Ready!")
    yield
    logger.info("👋 Shutting down...")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Customer Support Copilot API",
    description="AI-powered support agent with RAG, persistent memory, and tool calling.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Schemas ──────────────────────────────────────────────────────────
class CreateTicketRequest(BaseModel):
    customer_id: str
    customer_email: str
    subject: str
    body: str
    priority: Optional[TicketPriority] = TicketPriority.medium


class UpdateStatusRequest(BaseModel):
    status: TicketStatus


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "customer-support-copilot"}


@app.post("/tickets/", status_code=201)
async def create_ticket(req: CreateTicketRequest, db: AsyncSession = Depends(get_db)):
    ticket = Ticket(
        customer_id=req.customer_id,
        customer_email=req.customer_email,
        subject=req.subject,
        body=req.body,
        priority=req.priority,
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    logger.info(f"Ticket #{ticket.id} created for customer {req.customer_id}")
    return ticket


@app.get("/tickets/")
async def list_tickets(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Ticket).order_by(Ticket.created_at.desc())
    if status:
        query = query.where(Ticket.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@app.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.post("/tickets/{ticket_id}/generate")
async def generate_ai_response(ticket_id: int, db: AsyncSession = Depends(get_db)):
    """
    Core AI endpoint — runs the support agent and stores the draft response.
    This is the one-click 'Generate AI Response' button in the dashboard.
    """
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    logger.info(f"🤖 Generating AI response for ticket #{ticket_id}...")

    try:
        ai_response = generate_response(
            customer_id=ticket.customer_id,
            ticket_subject=ticket.subject,
            ticket_body=ticket.body,
        )
    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    # Save the AI response and update status
    await db.execute(
        update(Ticket)
        .where(Ticket.id == ticket_id)
        .values(ai_response=ai_response, status=TicketStatus.in_progress)
    )
    await db.commit()

    return {"ticket_id": ticket_id, "ai_response": ai_response}


@app.put("/tickets/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: int,
    req: UpdateStatusRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    await db.execute(
        update(Ticket).where(Ticket.id == ticket_id).values(status=req.status)
    )
    await db.commit()
    return {"ticket_id": ticket_id, "status": req.status}


@app.get("/customers/")
async def list_customers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer))
    return result.scalars().all()
