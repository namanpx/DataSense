# AI Data Analyst Agent

A LangGraph-powered chatbot that answers natural-language questions by routing between structured data (SQL via DuckDB) and unstructured documents (RAG via ChromaDB), then synthesises a text answer and generates a Plotly chart when relevant.

> **Status:** Fully implemented and working. All nodes contain real logic for routing, SQL generation, validation, execution, RAG retrieval, synthesis, and chart generation.

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
| LLM | Groq Llama-3.3-70B (`llama-3.3-70b-versatile`) via `langchain-groq` |
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
#   GROQ_API_KEY=gsk_your-key-here
```

### 4. Run the pipeline smoke-test

Verifies graph structure, routing, and the SQL retry loop end-to-end.

```bash
PYTHONPATH=. python backend/agent/graph.py
```

Three test questions fire (sql / rag / hybrid). Watch the log lines to see which nodes fire in which order.

### 5. Start the FastAPI backend

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

### 6. Start the Streamlit frontend (in a second terminal)

```bash
streamlit run frontend/app.py
```

Open http://localhost:8501, type a question, and inspect the raw JSON state returned by the graph.

---

## Example Questions (Superstore Dataset)

To test the system against the included Superstore dataset, try these queries:

- **SQL:** "What is the total revenue by category?" (Will generate a DuckDB query and Plotly chart)
- **RAG:** "What is the return policy for electronics?" (Will query the ChromaDB document store)
- **Hybrid:** "Which region had the highest total sales in Q1 2024, and what are our strategic goals for that region?" (Will combine DB aggregation with document retrieval)

---

## Project Structure

```
data-analyst-agent/
├── backend/
│   ├── agent/
│   │   ├── state.py               # AgentState TypedDict
│   │   ├── graph.py               # Full LangGraph graph
│   │   └── nodes/
│   │       ├── parse_and_route.py # Classify question + conditional edge fns
│   │       ├── generate_sql.py    # Generate SQL from question
│   │       ├── validate_sql.py    # Validate SQL (with retry loop)
│   │       ├── execute_sql.py     # Execute SQL against DuckDB
│   │       ├── retrieve_docs.py   # ChromaDB document retrieval
│   │       ├── synthesize_answer.py # Build final answer with LLM
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

| Week | Focus | Status |
|------|-------|--------|
| **1** | Project scaffold, toy graph smoke-test, stub graph routing/retry proof | ✅ Done |
| **2** | Real `parse_and_route` (LLM classifier), real `retrieve_docs` (ChromaDB), real `generate_sql` + `validate_sql` + `execute_sql` (DuckDB) | ✅ Done |
| **3** | Real `synthesize_answer` (LLM) + real `generate_chart` (Plotly) | ✅ Done |
| **4** | Polish, error handling, streaming, deployment | 🚧 In Progress |

---

## Known limitations / what's next

- **No authentication:** Currently the API and UI are unauthenticated.
- **No streaming:** Responses wait for full generation before being returned.
- **Single-user & In-memory history:** The chat history is maintained in-memory for a single session and does not scale to multi-tenant persistent conversations yet.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | Groq API key |
| `OPENAI_API_KEY` | ⬜ Optional | Only needed for OpenAI embeddings |
