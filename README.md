# 🎧 AI-Powered Customer Support Copilot

> An intelligent, production-ready support agent that eliminates context-switching for support teams — combining RAG, persistent memory, and LangChain tool calling into a one-click response generator.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![LangChain](https://img.shields.io/badge/LangChain-0.3-orange)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-purple)
![Mem0](https://img.shields.io/badge/Mem0-Persistent_Memory-red)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue?logo=docker)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-black?logo=githubactions)

---

## 🚀 The Problem

Support agents lose **60%+ of their time** switching between CRM, billing systems, and knowledge bases before they can even begin drafting a reply. This project eliminates that entirely.

## 💡 The Solution

A one-click AI copilot that:
1. **Retrieves customer context** from CRM and billing systems via tool calling
2. **Searches the knowledge base** using semantic RAG (ChromaDB)
3. **Recalls past interactions** using persistent memory (Mem0)
4. **Drafts a complete, personalized response** — ready for agent review in seconds

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Streamlit Dashboard                  │
│         (Ticket Queue | New Ticket | Analytics)      │
└────────────────────┬────────────────────────────────┘
                     │ HTTP
┌────────────────────▼────────────────────────────────┐
│                  FastAPI Backend                     │
│              POST /tickets/{id}/generate             │
└────┬──────────────┬──────────────┬──────────────────┘
     │              │              │
┌────▼────┐  ┌──────▼──────┐  ┌───▼────────────┐
│  Mem0   │  │  ChromaDB   │  │ LangChain Agent│
│ Memory  │  │  RAG Search │  │  + Tool Calling│
└─────────┘  └─────────────┘  └───┬────────────┘
                                   │
                          ┌────────┴────────┐
                          │                 │
                    ┌─────▼─────┐   ┌───────▼───┐
                    │ CRM Tool  │   │Billing Tool│
                    └───────────┘   └───────────┘
```

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | OpenAI GPT-4o-mini |
| Agent Framework | LangChain + OpenAI Tools Agent |
| Persistent Memory | Mem0 |
| Vector Store | ChromaDB |
| Backend | FastAPI + SQLAlchemy + SQLite |
| Frontend | Streamlit |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions → AWS EC2 |

---

## ⚡ Quick Start

### 1. Clone & configure
```bash
git clone https://github.com/YOUR_USERNAME/customer-support-copilot.git
cd customer-support-copilot
cp .env.example .env
# Add your OPENAI_API_KEY and MEM0_API_KEY to .env
```

### 2. Run with Docker (recommended)
```bash
docker compose up --build
```
- Backend API: http://localhost:8000
- Streamlit UI: http://localhost:8501
- API Docs:     http://localhost:8000/docs

### 3. Run locally (without Docker)
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔑 Required API Keys

| Key | Where to Get It |
|---|---|
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com) |
| `MEM0_API_KEY` | [app.mem0.ai](https://app.mem0.ai) (free tier available) |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/tickets/` | List all tickets |
| `POST` | `/tickets/` | Create a new ticket |
| `GET` | `/tickets/{id}` | Get ticket by ID |
| `POST` | `/tickets/{id}/generate` | 🤖 Generate AI response |
| `PUT` | `/tickets/{id}/status` | Update ticket status |
| `GET` | `/customers/` | List all customers |

Interactive docs available at `/docs` (Swagger UI).

---

## 🧠 How the Agent Works

When `POST /tickets/{id}/generate` is called:

1. **RAG Search** — Queries ChromaDB for knowledge base articles relevant to the ticket
2. **Memory Recall** — Fetches past interaction summaries for the customer from Mem0
3. **Agent Reasoning** — LangChain agent decides which tools to call:
   - `get_customer_crm_info(customer_id)` — fetches name, plan, account manager
   - `get_billing_info(customer_id)` — fetches payment status and invoices
4. **Response Generation** — GPT-4o-mini synthesizes all context into a draft response
5. **Memory Update** — Interaction is saved to Mem0 for future context

---

## 🗂️ Project Structure

```
customer-support-copilot/
├── backend/
│   ├── main.py                  # FastAPI application & routes
│   ├── agent/
│   │   └── support_agent.py     # Core LangChain agent
│   ├── memory/
│   │   └── mem0_client.py       # Mem0 memory client
│   ├── rag/
│   │   └── knowledge_base.py    # ChromaDB vector store
│   ├── tools/
│   │   ├── crm_tool.py          # CRM lookup tool
│   │   └── billing_tool.py      # Billing lookup tool
│   ├── database/
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   └── db.py                # DB init and session
│   └── requirements.txt
├── frontend/
│   └── app.py                   # Streamlit dashboard
├── .github/workflows/
│   └── ci-cd.yml                # GitHub Actions pipeline
├── docker-compose.yml
└── .env.example
```

---

## 🚢 CI/CD Pipeline

```
Push to main
    ↓
Lint (flake8) + Tests
    ↓
Build Docker Images → Docker Hub
    ↓
SSH Deploy → AWS EC2 (docker compose up)
```

To enable: add `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY` as GitHub repository secrets.

---

## 🙋 Author

**Aryan Rajguru**
- 🌐 [aryanrajguru.com](https://aryanrajguru.com)
- 💼 [LinkedIn](https://linkedin.com/in/aryanrajguru)
- 🐙 [GitHub](https://github.com/YOUR_USERNAME)
