# RAVAND OS – Offline AI Operating System

> **جایی که ایده‌ها جان می‌گیرن**  
> A production-grade offline AI operating system built for FabLab Ravand / TPE Co.

---

## Overview

RAVAND OS is a fully offline, fully local AI operating system that runs on Windows.  
It uses **Ollama** as the sole AI engine – no cloud, no API keys, no internet dependency.

Built with Python 3.12+, FastAPI, SQLAlchemy, and SQLite.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      FastAPI Layer                       │
│  /health  /api/v1/chat  /api/v1/agent  /api/v1/memory  │
└─────────────────────────────┬───────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────┐
│                   Application Services                   │
│  AIService  MemoryService  AgentService  PluginService  │
│  SessionService  KnowledgeService                       │
└──────────┬──────────────┬──────────────┬────────────────┘
           │              │              │
    ┌──────▼──────┐ ┌────▼────┐  ┌─────▼──────┐
    │   Ollama    │ │ SQLite  │  │  Plugin     │
    │ :11434      │ │   DB    │  │  System     │
    └─────────────┘ └─────────┘  └────────────┘
```

### Layers

| Layer | Location | Responsibility |
|-------|----------|---------------|
| API | `app/api/` | HTTP routing, request/response validation |
| Application | `app/services/` | Business logic, orchestration |
| Domain | `app/database/models.py`, `app/schemas/` | Data models, validation |
| Infrastructure | `app/database/`, Ollama HTTP | Persistence, AI inference |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app + lifespan
│   ├── api/
│   │   └── v1/
│   │       ├── router.py          # Aggregates all v1 routers
│   │       └── endpoints/
│   │           ├── health.py      # GET /health
│   │           ├── chat.py        # POST /api/v1/chat
│   │           ├── company.py     # GET /api/v1/company
│   │           ├── models.py      # GET /api/v1/models
│   │           ├── agent.py       # POST /api/v1/agent
│   │           └── memory.py      # POST/GET /api/v1/memory
│   ├── core/
│   │   ├── config.py              # Pydantic Settings (from .env)
│   │   └── logging.py             # Rotating file + console logging
│   ├── database/
│   │   ├── database.py            # Engine, SessionLocal, init_db
│   │   ├── models.py              # All SQLAlchemy ORM models
│   │   └── session.py             # Re-export surface
│   ├── schemas/
│   │   ├── chat_schema.py         # Chat request/response schemas
│   │   └── company_schema.py      # Health/Company schemas
│   ├── services/
│   │   ├── ai_service.py          # Ollama HTTP client (ONLY AI interface)
│   │   ├── memory_service.py      # Short-term + long-term memory
│   │   ├── knowledge_service.py   # System prompt + RAG-ready knowledge
│   │   ├── agent_service.py       # Multi-agent framework
│   │   ├── session_service.py     # ChatSession CRUD
│   │   └── plugin_service.py      # Plugin loader, registry, event bus
│   ├── crud/                      # Future CRUD modules
│   └── utils/
│       └── helpers.py             # Text, hash, timing utilities
├── plugins/
│   └── system_info_plugin.py      # Example plugin
├── logs/                          # Auto-created at runtime
├── run.py                         # Convenience launcher
├── requirements.txt
├── .env.example
└── README.md
```

---

## Quick Start

### 1. Prerequisites

- Python 3.12+
- [Ollama](https://ollama.ai) installed and running
- The model pulled: `ollama pull gpt-oss:20b`

### 2. Install dependencies

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work out of the box)
```

### 4. Start Ollama

```bash
ollama serve
# In a separate terminal:
ollama pull gpt-oss:20b
```

### 5. Run RAVAND OS

```bash
python run.py
```

Or directly with uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Access

| URL | Description |
|-----|-------------|
| http://localhost:8000/docs | Interactive API docs (Swagger UI) |
| http://localhost:8000/health | System health check |
| http://localhost:8000/redoc | ReDoc documentation |

---

## API Reference

### GET /health

Returns status of all subsystems (Ollama, database).

```json
{
  "status": "ok",
  "app_name": "RAVAND OS",
  "version": "1.0.0",
  "environment": "development",
  "uptime_seconds": 42.5,
  "ollama": {
    "reachable": true,
    "version": "0.3.x",
    "model_loaded": true,
    "available_models": ["gpt-oss:20b"]
  },
  "database": {
    "reachable": true,
    "url": "sqlite:///./ravand_os.db"
  }
}
```

---

### POST /api/v1/chat

Multi-turn conversation with the local AI.

**Request:**
```json
{
  "message": "Explain Newton's second law",
  "session_id": "optional-existing-session-uuid",
  "temperature": 0.7,
  "max_tokens": 2048
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "message_id": "uuid",
  "role": "assistant",
  "content": "Newton's second law states that F = ma...",
  "model": "gpt-oss:20b",
  "usage": {
    "prompt_tokens": 45,
    "completion_tokens": 312,
    "total_tokens": 357
  },
  "duration_ms": 1840,
  "created_at": "2025-01-01T12:00:00Z"
}
```

---

### POST /api/v1/agent

Invoke a specialised agent.

**Request:**
```json
{
  "agent": "engineering",
  "message": "What steel grade is best for CNC machined brackets?",
  "session_id": "optional-uuid",
  "temperature": 0.5
}
```

**Available agents:**

| Agent | Specialisation |
|-------|---------------|
| `general` | General-purpose assistant |
| `coding` | Python, FastAPI, software engineering |
| `engineering` | Mechanical / structural engineering, CNC, 3D printing |
| `design` | Industrial design, ergonomics, DFM |
| `task_automation` | Project planning, workflow automation |

---

### GET /api/v1/models

Lists all models available in the local Ollama instance.

---

### POST /api/v1/memory

Store a long-term memory record.

```json
{
  "content": "Customer prefers PLA for structural prototypes",
  "memory_type": "preference",
  "importance": 0.8,
  "tags": ["customer", "materials", "3d-printing"]
}
```

### GET /api/v1/memory/search?query=PLA

Search long-term memory.

---

## Configuration

All settings are loaded from `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `gpt-oss:20b` | Default model |
| `OLLAMA_TIMEOUT` | `120` | Request timeout (seconds) |
| `OLLAMA_MAX_RETRIES` | `3` | Retry attempts on failure |
| `DATABASE_URL` | `sqlite:///./ravand_os.db` | SQLAlchemy connection string |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DEBUG` | `false` | Enable debug mode |
| `ENVIRONMENT` | `development` | Runtime environment |

---

## Plugin System

RAVAND OS supports plugins that extend functionality without modifying core code.

### Creating a Plugin

1. Create a `.py` file in `backend/plugins/`
2. Define a class named `Plugin` that inherits from `BasePlugin`
3. Implement `on_load()` and `on_unload()`
4. Restart RAVAND OS – the plugin loads automatically

```python
from app.services.plugin_service import BasePlugin, EventBus

class Plugin(BasePlugin):
    NAME = "my_plugin"
    VERSION = "1.0.0"
    DESCRIPTION = "My custom RAVAND OS plugin."

    def on_load(self) -> None:
        self.event_bus.subscribe("chat.message_received", self._handler)

    def on_unload(self) -> None:
        self.event_bus.unsubscribe("chat.message_received", self._handler)

    def _handler(self, payload: dict) -> None:
        print(f"Message received: {payload}")
```

### Available Events

| Event | Payload | Description |
|-------|---------|-------------|
| `plugin.loaded` | `{name, version}` | A plugin was loaded |
| `plugin.unloaded` | `{name}` | A plugin was unloaded |
| `chat.message_received` | `{session_id, content}` | Chat message incoming |
| `memory.stored` | `{id, memory_type}` | Memory record stored |
| `task.completed` | `{id, title}` | Task completed |

---

## Database Schema

| Table | Purpose |
|-------|---------|
| `users` | Local user profiles |
| `chat_sessions` | Conversation containers |
| `chat_messages` | Individual messages |
| `memory_records` | Long-term memory storage |
| `tasks` | Task automation records |
| `app_logs` | Structured application event log |

### Migrating to PostgreSQL

Change only `.env`:

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/ravand_os
```

No code changes required.

---

## Memory System

```
User Message
     │
     ▼
Short-Term Memory (in-process)
  └── Last 20 turns per session
  └── Named facts per session
     │
     ▼ (auto-compress at 40+ turns)
Long-Term Memory (SQLite)
  └── Summaries
  └── Facts
  └── Preferences
  └── Search via full-text (upgrade to vector search anytime)
```

---

## Future Expansion

The architecture is designed for these planned modules:

| Module | Status | Notes |
|--------|--------|-------|
| Vision AI | Planned | Ollama multimodal models |
| Speech-to-Text | Planned | Whisper local |
| Text-to-Speech | Planned | Coqui / Piper local |
| CAD Assistant | Planned | Engineering agent extension |
| File Intelligence | Planned | Plugin-based |
| Automation Workflows | Planned | TaskAutomationAgent extension |
| Desktop Integration | Planned | Windows tray app |
| Vector Memory | Planned | Replace SQLite LIKE with FAISS |
| Knowledge Base | Planned | Markdown + PDF ingestion |

---

## Logs

Logs are written to the `logs/` directory:

| File | Content |
|------|---------|
| `ravand_os.log` | All application logs |
| `ravand_os_errors.log` | WARNING and above only |

Log files rotate automatically at 10 MB with 5 backups.

---

## Development

```bash
# Install dev dependencies
pip install black ruff mypy pytest httpx

# Format code
black app/

# Lint
ruff check app/

# Type check
mypy app/

# Run tests
pytest tests/
```

---

## Credits

Built for **FabLab Ravand** / **TPE Co.**  
Zahedan, Iran – Nogam Science and Technology Park  
Powered entirely by local Ollama inference.

---

*RAVAND OS – Offline. Local. Yours.*
