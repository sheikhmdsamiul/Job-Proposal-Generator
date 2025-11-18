# Job-Proposal-Generator

Swiftme Mini — a local-first job proposal generator that converts a freelancer profile
into an embedding-backed knowledge base and generates tailored proposals for job
postings using a RAG (retrieval-augmented generation) workflow.

This repository contains a small FastAPI backend that ingests a `FreelancerProfile`,
persists embeddings to a local FAISS vector store, analyzes job postings with a
local Ollama LLM, and composes proposals using the same LLM.

Contents
- `app/` — FastAPI app and services (vector store, job analyzer, proposal generator).
- `example_usage.py` — simple script showing API usage (profile setup, proposal generation, history).
- `requirements.txt` — Python dependencies.
- `envfile/` — included virtualenv snapshot (optional; you can create your own venv).

Key points
- Vector DB: FAISS (local). The project previously used Chroma; environment variables named
	`CHROMA_DIR` and `CHROMA_COLLECTION` are retained for backward compatibility and now point
	to where FAISS data is stored (default `./chroma_db`).
- Embeddings & LLM: Ollama (local). Uses `nomic-embed-text` (embeddings) and a local LLM
	(default `llama3:8b-instruct` / `llama2:7b` depending on env).

Prerequisites
- Python 3.10+ (3.12 tested in this environment).
- Ollama installed and running locally: https://ollama.ai
	- Pull required models: `ollama pull nomic-embed-text` and `ollama pull llama3:8b-instruct` (or your preferred models).
- FAISS: `faiss-cpu` package. On Windows installing `faiss-cpu` via pip may fail — see notes below.

Setup (recommended: PowerShell)

1. Create and activate a venv (or use `envfile` if you want to reuse the included snapshot):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install Python dependencies:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```


3. Ensure Ollama is running and models are pulled:

```powershell
# start ollama daemon if needed (depends on your installation)
# ollama serve
# then pull models
ollama pull nomic-embed-text
ollama pull llama2:7b
```

Configuration (env)
- `OLLAMA_LLM_MODEL` — Ollama LLM model (default: `llama2:7b`).
- `OLLAMA_EMBED_MODEL` — Embedding model (default: `nomic-embed-text`).
- `CHROMA_DIR` — directory used for vector store persistence (default: `./chroma_db`).
- `CHROMA_COLLECTION` — logical collection name (default: `freelancer_profiles`).

There is a `.env.example` in `app/` showing these settings. The code keeps the
`CHROMA_*` names to avoid breaking configuration, but the implementation now uses FAISS.

Run the API

```powershell
python -m uvicorn app.main:app --reload 
```

Open the docs UI at `http://127.0.0.1:8000/docs` after the server starts.

API Endpoints
- `POST /api/profile/setup` — body: `ProfileSetupRequest` (see `app/models.py`).
	- Converts the profile to text, splits it into chunks, embeds with Ollama embeddings, and stores them in FAISS.
	- Response: `{ "success": true, "message": "Profile successfully stored in knowledge base" }`
- `POST /api/proposal/generate` — body: `ProposalGenerationRequest` (job_posting, tone, custom_instructions).
	- Workflow: analyze job posting (Ollama) -> build search query -> retrieve top-k chunks from FAISS -> compose prompt -> generate proposal (Ollama).
	- Response: `ProposalGenerationResponse` with `proposal`, `confidence_score`, `matched_skills`, `timestamp`.
- `GET /api/proposal/history` — returns last 5 generated proposals.

Example usage
1. Start the server (see above).
2. Run the example script in a separate terminal while the server is running:

```powershell
python example_usage.py
```

This script will:
- POST `/api/profile/setup` with a sample profile
- POST `/api/proposal/generate` with a sample job posting and print the returned proposal
- GET `/api/proposal/history` to show saved proposals

Troubleshooting
- Error: "'ChatOllama' object is not callable" — fixed in this repo by using the `.invoke(...)`
	method on `ChatOllama` instead of calling the instance directly. If you see this error, ensure
	you have the latest local copy of the repo.
- Ollama connection errors: ensure Ollama is running locally and the requested models are present.
- FAISS install errors on Windows: use conda as shown above or run in WSL/Linux.
- Unresolved imports in editors (e.g., `langchain.schema` not resolved): make sure the
	venv used by your editor has `langchain` and `langchain-ollama` installed.

Development notes
- Vector store implementation: `app/services/vector_store.py` — uses FAISS via
	`langchain` wrappers; embeddings come from Ollama via `OllamaEmbeddings`.
- Job analyzer: `app/services/job_analyzer.py` — extracts structured job requirements
	using Ollama and a Pydantic output parser.
- Proposal generator: `app/services/proposal_generator.py` — builds a prompt, calls Ollama,
	and returns a `GeneratedProposal` object (contains `confidence_score` and `matched_skills`).

Notes about the migration from Chroma → FAISS
- The project originally used Chroma for persistence. To minimize configuration churn, the
	env vars kept the `CHROMA_*` names but FAISS is used under the hood now. FAISS data is
	persisted to the directory pointed at by `CHROMA_DIR` (default `./chroma_db`).

Next steps / ideas
- Add unit tests and CI that mock Ollama for reproducible runs.
- Add a lightweight web UI to compose job postings and view generated proposals.
- Add profile versioning and support for multiple profiles/collections.

