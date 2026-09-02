# Backend Architecture — Sovereign AI Workbench

## Overview

The backend is a **FastAPI** application that provides a REST API layer
for the Sovereign AI Workbench.  It sits alongside the existing Streamlit
frontend and introduces clean separation of concerns for all future
development phases.

```
sovereign-ai/
├── app.py                    # Streamlit frontend (unchanged)
├── backend/                  # FastAPI backend
│   ├── __init__.py
│   ├── main.py               # Application factory + uvicorn entry
│   ├── config.py             # Pydantic Settings (env-driven)
│   ├── logging_config.py     # Structured logging setup
│   ├── exceptions.py         # Custom exceptions + global handlers
│   ├── dependencies.py       # FastAPI auth & RBAC injection dependencies
│   ├── api/                  # HTTP routing layer
│   │   ├── health.py         # GET /api/v1/health (functional)
│   │   ├── auth.py           # Phase 2: Login, Register, Me (functional)
│   │   ├── security.py       # Phase 2: Classify, Evaluate (functional)
│   │   ├── documents.py      # Phase 3 placeholder
│   │   ├── models.py         # Phase 5 placeholder
│   │   ├── agents.py         # Phase 6 placeholder
│   │   ├── governance.py     # Phase 7 placeholder
│   │   ├── audit.py          # Phase 8 placeholder
│   │   └── deliverables.py   # Phase 9 placeholder
│   ├── schemas/              # Pydantic request/response models
│   │   ├── common.py         # ApiResponse[T], ErrorResponse
│   │   ├── health.py         # HealthResponse, ComponentStatus
│   │   ├── auth.py           # UserLogin, UserCreate, TokenResponse, UserResponse
│   │   └── security.py       # ClassifyRequest, EvaluatePolicyRequest, PolicyResult
│   ├── services/             # Business logic layer
│   │   ├── health.py         # HealthService (Ollama/ChromaDB/disk)
│   │   ├── auth.py           # AuthService (JWT + JSON user store)
│   │   ├── rbac.py           # RBACService (roles.json resolver)
│   │   └── security.py       # SecurityService (wraps core.security.SecurityEngine)
│   └── data/                 # Security data stores
│       ├── roles.json        # RBAC role -> permission mapping
│       ├── users.json        # Local user store (auto-seeded admin)
│       └── users.json.example
├── core/                     # Existing agent/security modules (preserved)
├── document/                 # Existing parser/OCR modules (preserved)
├── rag/                      # Existing vector store modules (preserved)
├── config/                   # Existing model config JSON
├── data/                     # Knowledge, vector DB, uploads
├── audit/                    # Audit trail (events.jsonl)
└── tests/                    # Pytest test suite
    ├── test_auth.py          # Auth API & token tests
    ├── test_rbac.py          # Role & permission enforcement tests
    └── test_security.py      # Classification & policy engine tests
```

## Layer Separation

```
┌──────────────────────────────────────────────────────────┐
│                    API Layer (api/)                       │
│  Thin HTTP routing — request parsing, response shaping   │
│  Each file = one APIRouter for a domain area             │
├──────────────────────────────────────────────────────────┤
│                  Service Layer (services/)                │
│  Business logic — AuthService, RBACService, SecuritySvc  │
│  Wraps existing core/, document/, rag/ modules.           │
├──────────────────────────────────────────────────────────┤
│                  Schema Layer (schemas/)                  │
│  Pydantic models for validation and serialisation.       │
│  Shared across API and Service layers.                   │
├──────────────────────────────────────────────────────────┤
│               Configuration (config.py)                  │
│  Pydantic BaseSettings loaded from .env with defaults.   │
│  All paths resolved from project root.                   │
├──────────────────────────────────────────────────────────┤
│            Existing Modules (core/ document/ rag/)       │
│  Preserved as-is.  Services wrap them progressively.     │
└──────────────────────────────────────────────────────────┘
```

## Running the Backend

```bash
# From the sovereign-ai/ directory:
cd sovereign-ai

# Install dependencies:
pip install -r requirements.txt

# Run test suite:
python -m pytest tests/ -v

# Start the API server:
python -m uvicorn backend.main:app --reload

# The server starts at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
# ReDoc at http://localhost:8000/redoc
```

## API Endpoints

### Functional (Phase 1 & Phase 2)

| Method | Path | Auth / Role | Description |
|--------|------|-------------|-------------|
| `GET` | `/api/v1/health` | None | System health check — probes Ollama, ChromaDB, disk |
| `POST` | `/api/v1/auth/login` | None | Authenticate with username/password, receive JWT token |
| `POST` | `/api/v1/auth/register` | JWT (`manage_users`) | Register a new user (ADMIN only) |
| `GET` | `/api/v1/auth/me` | JWT | Get current authenticated user profile |
| `POST` | `/api/v1/security/classify` | JWT | Classify text sensitivity (`GENERAL`, `INTERNAL`, `CONFIDENTIAL`) |
| `POST` | `/api/v1/security/evaluate` | JWT | Evaluate policy decision (`ALLOW`, `MASK`, `TOKENIZE`, `RESTRICT`) |

### Placeholder (returns 501)

| Method | Path | Phase |
|--------|------|-------|
| `GET` | `/api/v1/documents` | Phase 3 |
| `POST` | `/api/v1/documents/upload` | Phase 3 |
| `GET` | `/api/v1/models` | Phase 5 |
| `POST` | `/api/v1/agents/execute` | Phase 6 |
| `GET` | `/api/v1/agents/status/{task_id}` | Phase 6 |
| `GET` | `/api/v1/governance/pending` | Phase 7 |
| `POST` | `/api/v1/governance/approve/{task_id}` | Phase 7 |
| `GET` | `/api/v1/audit/events` | Phase 8 |
| `POST` | `/api/v1/deliverables/generate` | Phase 9 |

## Security & RBAC Architecture

### 1. Authentication
- Local JWT-based authentication using `pyjwt` signed with `JWT_SECRET_KEY` (HS256).
- User store maintained locally in `backend/data/users.json` (passwords hashed with `pbkdf2_sha256`).
- Automatic seeding of initial `admin` user (`admin123`) on first startup.

### 2. Role-Based Access Control (RBAC)
- Role definitions loaded from `backend/data/roles.json`.
- Configurable roles:
  - **ADMIN:** All permissions (upload, execute, approve, audit, manage users/models/knowledge).
  - **ENGINEER:** Upload documents, execute agents, use tools, manage knowledge.
  - **REVIEWER:** Approve actions, view audit, retrieve knowledge.
  - **OPERATOR:** Upload documents, execute agents, use tools, retrieve knowledge.
- Centralized authorization via FastAPI dependency `require_permission("permission_name")`. No hardcoded scattered authorization checks.

### 3. Security Classification & Policy Engine
- Wraps `core.security.SecurityEngine` keyword scoring to classify data as `GENERAL`, `INTERNAL`, or `CONFIDENTIAL`.
- Policy Evaluation maps classifications and actions to decisions:
  - **ALLOW:** Local processing permitted.
  - **MASK:** Sensitivity masking required for internal fields.
  - **TOKENIZE:** Data tokenization required.
  - **RESTRICT:** Confidential workflows restricted; external cloud AI calls explicitly forbidden (`allow_external_ai=False`); high-risk actions require human approval (`require_human_approval=True`).
- **Sovereign Constraint:** All policy decisions strictly forbid external/cloud AI calls (`allow_external_ai=False`).

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | Sovereign AI Workbench | Application display name |
| `JWT_SECRET_KEY` | sovereign-dev-secret-change-in-production | Secret key for JWT signing |
| `JWT_ALGORITHM` | HS256 | JWT signing algorithm |
| `JWT_EXPIRY_MINUTES` | 480 | JWT token lifetime (minutes) |
| `USERS_FILE` | backend/data/users.json | User store JSON file path |
| `ROLES_FILE` | backend/data/roles.json | RBAC roles JSON file path |
| `OLLAMA_HOST` | http://localhost:11434 | Ollama API base URL |

## Exception Handling

Custom exception classes (`SovereignError` subclasses) map to HTTP status codes:
- `AuthenticationError` → 401 Unauthorized
- `AuthorisationError` → 403 Forbidden
- `NotImplementedError_` → 501 Not Implemented
