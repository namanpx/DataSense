# AI Data Analyst Agent

A LangGraph-powered chatbot that answers natural-language questions by routing between structured data (SQL via DuckDB) and unstructured documents (RAG via ChromaDB), then synthesises a text answer and generates a Plotly chart when relevant.

> **Week 1 status:** Graph skeleton with stub nodes. Real logic is added node-by-node from Week 2 onwards.

---

## Architecture

```
User Question
     │
     ▼
parse_and_route ──┬─ (sql/hybrid) ──► generate_sql ──► validate_sql ──┬─ (fail, retry) ──► generate_sql
                  │                                                     └─ (pass) ──────────► execute_sql ──┐
                  └─ (rag) ──► retrieve_docs ──────────────────────────────────────────────────────────────┤
                                                                                                           ▼
                                                                                                  synthesize_answer
                                                                                                           │
                                                                                                           ▼
                                                                                                   generate_chart
                                                                                                           │
                                                                                                          END
```

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph |
| LLM | Anthropic Claude (`claude-opus-4-5`) |
| Structured data | DuckDB (file-based, no server) |
| Vector store / RAG | ChromaDB (embedded, local) |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Charts | Plotly |
| Language | Python 3.11+ |

---

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd data-analyst-agent
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env and set at minimum:
#   ANTHROPIC_API_KEY=sk-ant-...
```

### 4. Run the toy graph (Week 1 smoke-test)

Verifies that the LangGraph + Claude integration works end-to-end before anything else.

```bash
PYTHONPATH=. python backend/agent/toy_graph.py
```

You should see log lines for `echo_node` and `llm_call_node`, followed by the final state with a real Claude answer.

### 5. Run the stub graph smoke-test

Verifies graph structure, routing, and the SQL retry loop.

```bash
PYTHONPATH=. python backend/agent/graph.py
```

Three test questions fire (sql / rag / hybrid). Watch the log lines to see which nodes fire in which order.

### 6. Start the FastAPI backend

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

### 7. Start the Streamlit frontend (in a second terminal)

```bash
streamlit run frontend/app.py
```

Open http://localhost:8501, type a question, and inspect the raw JSON state returned by the graph.

---

## Project Structure

```
data-analyst-agent/
├── backend/
│   ├── agent/
│   │   ├── state.py               # AgentState TypedDict
│   │   ├── graph.py               # Full LangGraph graph (stub nodes)
│   │   ├── toy_graph.py           # Minimal 3-node smoke-test graph
│   │   └── nodes/
│   │       ├── parse_and_route.py # Classify question + conditional edge fns
│   │       ├── generate_sql.py    # Generate SQL from question
│   │       ├── validate_sql.py    # Validate SQL (with retry loop)
│   │       ├── execute_sql.py     # Execute SQL against DuckDB
│   │       ├── retrieve_docs.py   # ChromaDB document retrieval
│   │       ├── synthesize_answer.py # Build final answer with Claude
│   │       └── generate_chart.py  # Generate Plotly chart
│   ├── main.py                    # FastAPI app (POST /ask)
│   └── requirements.txt
├── frontend/
│   └── app.py                     # Streamlit chat UI
├── data/                          # Datasets (gitignored except .gitkeep)
├── .env.example
├── .gitignore
└── README.md
```

---

## Roadmap

| Week | Focus |
|------|-------|
| **1 (now)** | Project scaffold, toy graph smoke-test, stub graph routing/retry proof |
| **2** | Real `parse_and_route` (LLM classifier), real `retrieve_docs` (ChromaDB), real `generate_sql` + `validate_sql` + `execute_sql` (DuckDB) |
| **3** | Real `synthesize_answer` (Claude) + real `generate_chart` (Plotly) |
| **4** | Polish, error handling, streaming, deployment |

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ Yes | Claude API key |
| `OPENAI_API_KEY` | ⬜ Optional | Only needed for OpenAI embeddings |
