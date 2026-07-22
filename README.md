# DataSense — Sovereign AI Data Analyst & Hybrid RAG Engine

DataSense is an autonomous, full-stack AI data analyst and hybrid RAG knowledge assistant designed to bridge the gap between non-technical decision-makers and enterprise datasets. Built using **LangGraph**, **FastAPI**, **DuckDB**, **ChromaDB**, and **Next.js 16**, DataSense accepts plain English questions and intelligently routes them to either an in-memory SQL analytical engine or a dense vector retrieval system (RAG).

> **Live Application**: [https://datasense-final.vercel.app](https://datasense-final.vercel.app)  
> **Live Backend API**: [https://datasense-lqwi.onrender.com](https://datasense-lqwi.onrender.com)  
> **GitHub Repository**: [https://github.com/namanpx/DataSense.git](https://github.com/namanpx/DataSense.git)

---

## 🏗️ Architecture

```
                       [User Natural Language Query / File Upload]
                                            │
                                            ▼
                           [Next.js 16 Sovereign Terminal UI]
                                            │ (REST API / JSON)
                                            ▼
                                 [FastAPI Backend Server]
                                            │
                                   [LangGraph Router]
                                  /                  \
                                 /                    \
                            [SQL Branch]          [RAG Branch]
                                 │                     │
                    [DuckDB Schema Introspection]  [ChromaDB Vector Search]
                                 │                     │
                    [Llama 3.3 SQL Synthesis]      [Context Retrieval]
                                 │                     │
                     [DuckDB Query Execution]     [Answer Synthesis]
                      (Self-Correction Loop)           │
                                 │                     │
                     [Plotly Chart Engine]             │
                                 \                     /
                                  \                   /
                               [Consolidated Terminal Response]
```

---

## ⚡ Complete Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Frontend Framework** | **Next.js** | `16.0.0+` (App Router) | High-performance React framework for terminal UI |
| **UI Components** | **React** | `19.0.0` | Client-side reactive state management |
| **Styling & Aesthetics** | **Tailwind CSS** | `v4` | Sovereign Cyberpunk dark-mode design system |
| **Visualization Engine** | **Plotly.js** (`react-plotly.js`) | `2.35.3` | Dynamic interactive charts with peak bar highlighting |
| **Backend API Gateway** | **FastAPI** | `0.115.0+` | Asynchronous REST API server & multipart file receiver |
| **ASGI Server** | **Uvicorn** | `0.30.0+` | High-throughput async server execution |
| **Agent Orchestration** | **LangGraph** | `0.2.0+` | Stateful cyclic state machine for routing & self-correction |
| **LLM Integration** | **LangChain Core / Groq** | `0.3.0+` | Prompt templates & low-latency LLM bindings |
| **AI LLM Engine** | **Meta Llama 3.3 70B** | `llama-3.3-70b-versatile` | Zero-shot SQL generation, intent routing, and synthesis |
| **AI Hardware Acceleration** | **Groq LPUs** | Hardware API | Sub-second inference acceleration |
| **Analytical Database** | **DuckDB** | `1.2.0` | Embedded columnar OLAP SQL database for fast aggregates |
| **Vector Database** | **ChromaDB** | `0.6.0+` | Embedded dense vector database for RAG document retrieval |
| **Embedding Model** | **Sentence-Transformers** | `all-MiniLM-L6-v2` | 384-dimensional dense semantic vector extraction |
| **Data Processing** | **Pandas** | `2.2.3` | Data cleaning & multi-encoding CSV normalization |
| **Document Processing** | **PyPDF / TextSplitters** | `5.3.0` | PDF text extraction & recursive character text chunking |
| **Backend Cloud Host** | **Render Cloud** | Python 3.11.9 | Production backend container microservice |
| **Frontend Cloud Host** | **Vercel Edge** | Node.js 22 | Global edge CDN frontend hosting |

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- **Python**: `3.11.9`
- **Node.js**: `v20+` or `v22+`
- **Groq API Key**: Free API key from [console.groq.com](https://console.groq.com)

---

### 1. Clone & Configure Repository

```bash
git clone https://github.com/namanpx/DataSense.git
cd DataSense
```

Create a `.env` file in the root directory:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

---

### 2. Backend Setup (FastAPI)

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Launch FastAPI backend server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
> Backend API docs will be available at: `http://localhost:8000/docs`

---

### 3. Frontend Setup (Next.js 16)

Open a **new terminal window** and run:

```bash
cd frontend-web

# Install frontend dependencies
npm install

# Start Next.js development server
npm run dev -- -p 3001
```
> Open your browser at: `http://localhost:3001`

---

## 📂 Project Structure

```
DataSense/
├── backend/
│   ├── main.py                  # FastAPI application endpoints & startup seeder
│   ├── seed.py                  # Non-blocking DuckDB background database seeder
│   ├── requirements.txt         # Slimmed backend dependencies
│   └── agent/
│       ├── state.py             # AgentState TypedDict schema
│       ├── graph.py             # LangGraph state machine & router definition
│       ├── db.py                # DuckDB schema introspection & query executor
│       ├── load_csv.py          # Multi-encoding CSV fallback & table builder
│       ├── ingest.py            # ChromaDB vector store chunker & embedder
│       └── nodes/
│           ├── parse_and_route.py   # Intent classification router
│           ├── generate_sql.py      # LLM SQL query synthesis
│           ├── validate_sql.py      # SQL validation & error retry loop
│           ├── execute_sql.py       # DuckDB execution node
│           ├── retrieve_docs.py     # ChromaDB vector similarity search
│           ├── synthesize_answer.py # Natural language answer builder
│           └── generate_chart.py    # Plotly visualization spec builder
├── frontend-web/
│   ├── components/
│   │   ├── ChatTerminal.tsx     # Sovereign Cyberpunk terminal interface
│   │   ├── UploadPanel.tsx      # Dual-dropzone structured & document upload UI
│   │   └── ChartPanel.tsx       # Dynamic Plotly client-side chart renderer
│   ├── lib/api.ts               # Typed REST API client (/ask, /upload/*, /sources)
│   ├── package.json             # Next.js 16 & React 19 dependencies
│   └── .env.production          # Production backend API target pointer
├── data/raw/superstore.csv      # Seed dataset for instant startup testing
├── render.yaml                  # Render Cloud infrastructure blueprint
├── .python-version              # Pinned Python version (3.11.9)
├── .env.example                 # Environment variable template
└── README.md                    # System documentation
```

---

## 🧪 Example Test Queries (Superstore Dataset)

- **SQL Aggregations**: *"What is the total revenue by category?"*
- **Rankings & Filters**: *"Top 5 customers by total profit in the West region?"*
- **Document Retrieval (RAG)**: *"What is the summary of the strategic growth document?"*
- **Hybrid Query**: *"Which category had the highest sales and what are our strategic targets for that category?"*

---

## 🔒 Responsible AI & Safety

1. **Deterministic Calculations**: SQL queries execute 100% inside DuckDB, ensuring mathematical accuracy without LLM calculation hallucinations.
2. **Context-Grounded RAG**: Prompts mandate strict document citations and return explicit fallbacks when data is missing.
3. **Read-Only Database Controls**: Only `SELECT` statements are permitted. Write and delete operations (`INSERT`, `UPDATE`, `DROP`) are strictly blocked.
4. **Transparent Verification**: Every response renders the full generated SQL query, execution timings, and route badges for human oversight.

---

## 👥 Team & Credits

- **Team Name**: DATA SENSE AND 11
- **Institution**: Indira Gandhi Delhi Technical University for Women (IGDTUW) — Department of Information Technology (SIP 2026)
- **Team Leader**: Anshul Singh
- **Team Members**: Naman Pandey, Devanshi K, Khushi Maurya, Kavyanjali Rout
