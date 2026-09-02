# Repository Audit: Sovereign On-Premise Agentic AI Workbench

**Date:** September 2, 2026  
**Project:** Sovereign On-Premise Agentic AI Workbench  
**Repository Scope:** `sovereign-ai/`  
**Audit Purpose:** Comprehensive inspection of current codebase architecture, existing components, technical debt, and integration roadmap prior to feature development.

---

## 1. Current Architecture

The existing repository implements a single-tenant prototype monolith centered around a **Streamlit** user interface (`sovereign-ai/app.py`). It demonstrates an end-to-end flow for processing confidential inspection documents using local machine learning models and vector databases.

```
+-----------------------------------------------------------------------------------+
|                                STREAMLIT UI (app.py)                              |
+-----------------------------------------------------------------------------------+
       |                                      |                               |
       v                                      v                               v
+------------------+                +--------------------+          +--------------------+
|  Doc Parser/OCR  |                |   Security Engine  |          | Local Vector Store |
| (fitz/pytesseract)                | (Keyword Matching) |          | (ChromaDB+MiniLM)  |
+------------------+                +--------------------+          +--------------------+
       |                                      |                               |
       +------------------+                   |                   +-----------+
                          |                   |                   |
                          v                   v                   v
                    +---------------------------------------------------+
                    |              SovereignAgent (agent.py)            |
                    +---------------------------------------------------+
                                              |
                                              v
                                    +--------------------+
                                    |    Ollama LLM      |
                                    | (qwen3 / qwen2.5)  |
                                    +--------------------+
                                              |
                                              v
                                    +--------------------+
                                    | Verifier (Length)  |
                                    +--------------------+
                                              |
                                              v
                                    +--------------------+
                                    | Streamlit Output & |
                                    |  Governance Gate   |
                                    +--------------------+
```

### Execution Flow:
1. **Document Ingestion:** Streamlit receives user uploaded PDF/Image files and saves them to `data/uploads/`.
2. **Text Extraction & OCR:** PDF text is extracted using PyMuPDF (`fitz`). If extracted text length is under 100 characters, it falls back to PyTesseract OCR (`ocr_pdf`).
3. **Security Classification:** `SecurityEngine` scans text against 8 hardcoded keywords to assign a sensitivity label (`CONFIDENTIAL`, `INTERNAL`, `GENERAL`).
4. **Model Selection:** `ModelRouter` reads `config/models.json` to select an Ollama model profile based on task type (`reasoning`, `vision`, `coding`).
5. **Knowledge Retrieval:** `LocalVectorStore` queries persistent ChromaDB storage (`data/vector_db`) using `sentence-transformers/all-MiniLM-L6-v2` embeddings for top-3 relevant context chunks.
6. **Local LLM Execution:** `SovereignAgent` constructs a prompt combining document text and retrieved knowledge context, invoking `ollama.chat()` locally.
7. **Verification & Risk Assessment:** `Verifier` checks output validity (prototype check based on response character count). `CONFIDENTIAL` classification triggers a `human_required` governance flag.
8. **UI Presentation & Deliverables:** Streamlit renders classification metrics, LLM answer, and governance buttons. `document.generator` provides a helper to export output to DOCX.

---

## 2. Existing Components

| Component File / Folder | Purpose | Current Status | Dependencies |
| :--- | :--- | :--- | :--- |
| [`sovereign-ai/app.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/app.py) | Streamlit web application & end-to-end pipeline orchestrator | **Functional Prototype** (Tightly coupled UI & logic) | `streamlit`, `pathlib`, `document.parser`, `document.ocr`, `rag.vectorstore`, `core.agent` |
| [`sovereign-ai/requirements.txt`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/requirements.txt) | Environment dependencies declaration | **Active** | `streamlit`, `ollama`, `chromadb`, `sentence-transformers`, `pymupdf`, `pytesseract`, `Pillow`, `python-docx`, `pandas`, `numpy` |
| [`sovereign-ai/.env`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/.env) | Environment configuration variables | **Empty** | None |
| [`sovereign-ai/README.md`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/README.md) | Project documentation | **Empty** | None |
| [`sovereign-ai/config/models.json`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/config/models.json) | Local LLM capability map (reasoning, vision, coding) | **Active** | `json`, `pathlib` |
| [`sovereign-ai/setup_knowledge.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/setup_knowledge.py) | Script to trigger knowledge base vector ingestion | **Functional Script** | `rag.ingest` |
| [`sovereign-ai/core/agent.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/core/agent.py) | `LocalLLM` wrapper & `SovereignAgent` prompt execution pipeline | **Active** | `ollama`, `core.model_router`, `core.verifier`, `core.security`, `core.provenance` |
| [`sovereign-ai/core/model_router.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/core/model_router.py) | Model selector reading capability JSON | **Active** | `json`, `pathlib` |
| [`sovereign-ai/core/security.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/core/security.py) | Keyword-based document sensitivity classifier | **Active Prototype** | None |
| [`sovereign-ai/core/verifier.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/core/verifier.py) | Output verification engine | **Stub** (checks answer length >= 50) | None |
| [`sovereign-ai/core/provenance.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/core/provenance.py) | File SHA-256 hashing & JSONL audit trail logger | **Partially Disconnected** | `hashlib`, `json`, `datetime`, `pathlib` |
| [`sovereign-ai/core/policy.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/core/policy.py) | Policy enforcement module | **Empty Stub** (`print("policy.py loaded")`) | None |
| [`sovereign-ai/document/parser.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/document/parser.py) | PDF text extractor | **Functional** | `fitz` (PyMuPDF) |
| [`sovereign-ai/document/ocr.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/document/ocr.py) | PDF page image conversion & Tesseract OCR fallback | **Functional** | `fitz`, `pytesseract`, `PIL`, `io` |
| [`sovereign-ai/document/generator.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/document/generator.py) | DOCX Approval Note builder | **Functional Helper** | `docx` (python-docx) |
| [`sovereign-ai/rag/vectorstore.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/rag/vectorstore.py) | Local vector store wrapper around ChromaDB persistent client | **Active** (Contains ID overwrite bug) | `chromadb`, `sentence_transformers` |
| [`sovereign-ai/rag/ingest.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/rag/ingest.py) | Batch loader for `data/knowledge/*.txt` files | **Functional** | `pathlib`, `rag.vectorstore` |
| [`sovereign-ai/rag/retriever.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/rag/retriever.py) | Advanced context retriever | **Empty Stub** (`print("retriever.py loaded")`) | None |
| [`sovereign-ai/utils/hashing.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/utils/hashing.py) | Hashing utilities | **Empty File** (0 bytes) | None |
| [`sovereign-ai/data/knowledge/Maintenance_SOP.txt`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/data/knowledge/Maintenance_SOP.txt) | Sample SOP reference document | **Active Data** | None |
| [`sovereign-ai/data/vector_db/`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/data/vector_db) | ChromaDB persistent SQLite vector database | **Active Data** | `chromadb` |
| [`sovereign-ai/audit/events.jsonl`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/audit/events.jsonl) | Log file for audit trail records | **Corrupted/Test Data** (contains `"vjhv"`) | None |

---

## 3. Already Implemented

The following features and pipelines are currently operational in the repository:

1. **PDF Parsing & OCR Engine:**
   - Extracting structured page text via PyMuPDF.
   - Automatic scanned-document detection and fallback to PyTesseract OCR rendering at 2x resolution matrix.
2. **Local Embedding & Vector Storage:**
   - Persistent ChromaDB database setup at `data/vector_db`.
   - Local dense vector embeddings via `SentenceTransformer("all-MiniLM-L6-v2")`.
   - Text document ingestion pipeline loading `.txt` files from `data/knowledge/`.
3. **Local Ollama Integration:**
   - `LocalLLM` interface executing chat completion requests against a locally hosted Ollama instance (`ollama.chat()`).
   - Configuration-driven model capability routing (`qwen3:4b` for reasoning, `qwen3-vl:2b` for vision, `qwen2.5-coder:3b` for coding).
4. **Basic Security & Governance Pipeline:**
   - Text classification engine calculating sensitivity score based on predefined corporate keywords.
   - Dynamic policy rule matching (`CONFIDENTIAL` requiring human approval, `INTERNAL` / `GENERAL` permitting auto-approval).
5. **Basic User Interface:**
   - Interactive Streamlit application supporting file uploads, task prompts, step-by-step status expanders, metrics visualization, and human governance action buttons.
6. **Deliverable Generation:**
   - Formatted Word document (`.docx`) generation for corrective maintenance approval notes.
7. **Provenance Utilities:**
   - SHA-256 file checksum calculation and JSONL record builder.

---

## 4. Missing Components

Compared against the target enterprise **Sovereign On-Premise Agentic AI Workbench**, the current codebase is missing key architectural pillars:

### A. Backend Core Architecture
- **REST API Framework:** No FastAPI/Flask application layer; backend logic is embedded directly inside Streamlit frontend handlers.
- **Async Execution & Queue:** No asynchronous task queue (e.g. Celery / Redis / RQ) for long-running document analysis or agent multi-step loops.

### B. Security, Authentication & Governance
- **User Authentication & Authorization:** Zero user identity, session management, OAuth2/JWT token verification, or password management.
- **Role-Based Access Control (RBAC):** No user roles (Admin, Auditor, Operator, Viewer) or document-level access permissions.
- **Strict Network Egress Controls:** No automated network interface monitoring, firewall hooks, or proxy guards enforcing complete air-gapped zero-egress.

### C. Advanced RAG & Vector Storage
- **Semantic Chunking & Processing:** Ingests entire text files without chunking, sliding windows, or overlap.
- **Hybrid Search & Re-ranking:** Lacks keyword (BM25) search, reciprocal rank fusion, or cross-encoder re-ranking.
- **Multi-Format Ingestion:** No native parsers for DOCX, XLSX, CSV, HTML, or structured JSON.

### D. Model Fabric & Health System
- **Ollama Connection & Health Management:** No fallback model routing if Ollama is unreachable, no GPU memory monitoring, no streaming output support.
- **Context Window Management:** No token counting or dynamic prompt truncation to prevent context window overflow.

### E. Agent Runtime & Tools
- **Agent Orchestration Framework:** Single-shot static prompt execution; lacks re-act loops, multi-step planning, state preservation, memory, or external tool execution (file system, database queries).

### F. Verification & HITL State Engine
- **Hallucination & Faithfulness Engine:** `Verifier` does not check factual consistency against context documents.
- **Approval Workflow Persistence:** UI buttons (`APPROVE`, `REJECT`) are state-transient and do not persist decisions or trigger workflow transitions in a database.

### G. Infrastructure & Testing
- **Containerization & Deployment:** No `Dockerfile`, `docker-compose.yml`, Podman spec, or systemd unit configs.
- **Testing Suite:** 0 unit tests, integration tests, or evaluation benchmarks.

---

## 5. Technical Debt / Problems

The audit revealed critical technical debt, bugs, and architectural flaws:

1. **Vector Document ID Collision Bug (`rag/vectorstore.py`):**
   ```python
   ids = [f"doc_{i}" for i in range(len(texts))]
   ```
   **Impact:** Every time `ingest_knowledge()` or `add_documents()` is called, document IDs reset to `doc_0`, `doc_1`, etc. This overwrites previous embeddings in ChromaDB rather than appending new documents.

2. **Disconnected Audit Logging (`core/agent.py` & `app.py`):**
   - `SovereignAgent.run()` collects `events` but never calls `Provenance.create_record()`.
   - Streamlit UI (`app.py`) displays "AUDIT ACTIVE" badge while audit logging is entirely unexecuted during task processing.
   - `audit/events.jsonl` currently contains corrupted non-JSON text (`"vjhv"`).

3. **Empty Stub Modules:**
   - [`core/policy.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/core/policy.py): Contains only `print("policy.py loaded")`.
   - [`rag/retriever.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/rag/retriever.py): Contains only `print("retriever.py loaded")`.
   - [`utils/hashing.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/utils/hashing.py): Empty 0-byte file.

4. **Hardcoded Execution Inputs:**
   - [`core/agent.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/core/agent.py#L54): Hardcodes filename `"inspection_report.pdf"` into `self.security.classify()`, ignoring the actual uploaded file's name.
   - [`core/agent.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/core/agent.py#L47): Hardcodes `task_type = "scanned_document"`, bypassing dynamic classification for standard text PDFs or code inputs.

5. **Fragile Relative Pathing:**
   - `ModelRouter` uses `Path("config/models.json")`.
   - `LocalVectorStore` uses `Path("data/vector_db")`.
   - If commands or scripts are executed outside the root `sovereign-ai/` directory, `FileNotFoundError` will be thrown.

6. **Trivial Security & Verification Rules:**
   - `SecurityEngine` uses simple string matching over 8 static words (`confidential`, `internal`, `plant`, etc.), making it vulnerable to obfuscation or false positives.
   - `Verifier` marks output as `PASSED` solely if `len(answer.strip()) >= 50`.

7. **Air-Gap / Egress Risk:**
   - `SentenceTransformer("all-MiniLM-L6-v2")` attempts to reach HuggingFace Hub on initial instantiation unless the model weights are pre-downloaded and stored locally.

---

## 6. Recommended Integration Plan

To transition from the current prototype to the target enterprise **Sovereign On-Premise Agentic AI Workbench**, existing files are mapped to future development phases:

```
+-----------------------------------------------------------------------------------+
| PHASE 1: CORE BACKEND (FastAPI App, Config Management, Async Engine)              |
+-----------------------------------------------------------------------------------+
       |
       v
+-----------------------------------------------------------------------------------+
| PHASE 2: SECURITY / RBAC (Policy Engine, JWT Auth, Role Permissions)             |
| -> Refactor: sovereign-ai/core/security.py, core/policy.py                        |
+-----------------------------------------------------------------------------------+
       |
       v
+-----------------------------------------------------------------------------------+
| PHASE 3: DOCUMENT INTELLIGENCE (Layout Parser, Multi-format OCR Pipeline)        |
| -> Refactor: sovereign-ai/document/parser.py, document/ocr.py                    |
+-----------------------------------------------------------------------------------+
       |
       v
+-----------------------------------------------------------------------------------+
| PHASE 4: PRIVATE RAG (Fixed Storage IDs, Chunking, Hybrid Retrieval)              |
| -> Refactor: sovereign-ai/rag/vectorstore.py, rag/ingest.py, rag/retriever.py     |
+-----------------------------------------------------------------------------------+
       |
       v
+-----------------------------------------------------------------------------------+
| PHASE 5: MODEL FABRIC / ROUTER (Ollama Health, Streaming, Failover)               |
| -> Refactor: sovereign-ai/core/model_router.py, config/models.json                |
+-----------------------------------------------------------------------------------+
       |
       v
+-----------------------------------------------------------------------------------+
| PHASE 6: AGENT RUNTIME (Multi-step Agent, Tools, State Machine)                   |
| -> Refactor: sovereign-ai/core/agent.py                                           |
+-----------------------------------------------------------------------------------+
       |
       v
+-----------------------------------------------------------------------------------+
| PHASE 7: VERIFICATION / HITL (Faithfulness Check, Persistent Workflow)            |
| -> Refactor: sovereign-ai/core/verifier.py                                        |
+-----------------------------------------------------------------------------------+
       |
       v
+-----------------------------------------------------------------------------------+
| PHASE 8: PROVENANCE / AUDIT / NO-EGRESS (Hash Chaining, Cryptographic Audit)      |
| -> Refactor: sovereign-ai/core/provenance.py, utils/hashing.py                     |
+-----------------------------------------------------------------------------------+
       |
       v
+-----------------------------------------------------------------------------------+
| PHASE 9: DELIVERABLES (Template Generator, DOCX/PDF Export Engine)               |
| -> Refactor: sovereign-ai/document/generator.py                                   |
+-----------------------------------------------------------------------------------+
       |
       v
+-----------------------------------------------------------------------------------+
| PHASE 10: FRONTEND (Enterprise Dashboard, Audit Viewer, HITL Portal)              |
| -> Refactor: sovereign-ai/app.py                                                  |
+-----------------------------------------------------------------------------------+
       |
       v
+-----------------------------------------------------------------------------------+
| PHASE 11: INTEGRATION (Docker/Podman Deployment, E2E Tests, Air-gap Verification)  |
+-----------------------------------------------------------------------------------+
```

### Detailed Phase Mapping:

- **PHASE 1 — Core Backend:**
  - Build FastAPI backend structure (`backend/main.py`, `backend/api/`).
  - Move configuration parsing out of hardcoded JSON files into structured Pydantic settings.
- **PHASE 2 — Security/RBAC:**
  - Expand [`core/security.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/core/security.py) into multi-factor classification (regex, entity detection, sensitivity rules).
  - Implement full authorization rules in [`core/policy.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/core/policy.py).
- **PHASE 3 — Document Intelligence:**
  - Enhance [`document/parser.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/document/parser.py) and [`document/ocr.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/document/ocr.py) with layout preservation, table extraction, and error handling.
- **PHASE 4 — Private RAG:**
  - Fix document ID collisions in [`rag/vectorstore.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/rag/vectorstore.py).
  - Implement chunking and advanced hybrid search in [`rag/retriever.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/rag/retriever.py).
- **PHASE 5 — Model Fabric/Router:**
  - Enhance [`core/model_router.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/core/model_router.py) with live Ollama connection health checks and failover options.
- **PHASE 6 — Agent Runtime:**
  - Refactor [`core/agent.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/core/agent.py) into a modular, multi-turn agent with tool integration.
- **PHASE 7 — Verification/HITL:**
  - Overhaul [`core/verifier.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/core/verifier.py) to calculate semantic entailment scores against retrieved context.
- **PHASE 8 — Provenance/Audit/No-Egress:**
  - Integrate [`core/provenance.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/core/provenance.py) directly into the agent execution loop and populate [`utils/hashing.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/utils/hashing.py).
- **PHASE 9 — Deliverables:**
  - Upgrade [`document/generator.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/document/generator.py) into a multi-template document generation service.
- **PHASE 10 — Frontend:**
  - Decouple Streamlit UI ([`app.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/app.py)) to consume backend REST API endpoints rather than direct class imports.
- **PHASE 11 — Integration:**
  - Create Docker/Podman packaging files and setup integration test suites.

---

## Audit Summary

* **What Already Exists:** A working end-to-end prototype containing PyMuPDF/PyTesseract document parsing, ChromaDB local vector search, Ollama LLM chat integration (`qwen` models), basic keyword security classification, Streamlit web interface, and DOCX report generation.
* **What Is Missing:** Production REST API layer, authentication & RBAC, persistent database, advanced chunking & hybrid RAG, agent tool-calling/loops, real hallucination verification, persistent HITL workflows, containerization, and unit tests.
* **What Should Be Built First:** **Phase 1 (Core Backend Framework)** and **Phase 4 (RAG Vector Store ID Collision Fix & Chunking)** to provide a reliable API and vector database foundation before layering security, agents, and UI.
* **Files That Should NOT Be Modified Unnecessarily:**
  - Existing core working logic in [`document/parser.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/document/parser.py) and [`document/ocr.py`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/document/ocr.py) (functions work reliably and should be wrapped/extended rather than rewritten).
  - Data reference documents like [`data/knowledge/Maintenance_SOP.txt`](file:///c:/Users/sayak/OneDrive/Desktop/sovereign-ai/sovereign-ai/data/knowledge/Maintenance_SOP.txt).
