# AI Wrapper

AI SaaS platform that generates full web applications from natural language prompts.

## Architecture

```
User Prompt
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│  Frontend (Next.js + TailwindCSS)                        │
│  ┌──────────┐ ┌────────────┐ ┌────────────┐             │
│  │  Prompt   │ │   Monaco   │ │  Preview   │             │
│  │  Input    │ │   Editor   │ │  Panel     │             │
│  └──────────┘ └────────────┘ └────────────┘             │
└──────────────────────┬───────────────────────────────────┘
                       │ REST API
┌──────────────────────▼───────────────────────────────────┐
│  Backend (FastAPI)                                        │
│  ┌────────┐ ┌──────────┐ ┌───────────┐ ┌──────────────┐ │
│  │  Auth  │ │ Projects │ │  Deploy   │ │   Sandbox    │ │
│  │  API   │ │   API    │ │   API     │ │   Manager    │ │
│  └────────┘ └──────────┘ └───────────┘ └──────────────┘ │
│                    │                                      │
│  ┌─────────────────▼──────────────────────────────────┐  │
│  │  AI Agent Pipeline                                  │  │
│  │  Planner → Architect → FileGenerator → Debug        │  │
│  │                                    ↕                │  │
│  │                          Improvement Agent          │  │
│  └─────────────────────────────────────────────────────┘  │
└──────────────┬──────────────────┬────────────────────────┘
               │                  │
    ┌──────────▼──────┐  ┌───────▼──────────┐
    │   PostgreSQL    │  │  Docker Sandbox   │
    │   + Redis       │  │  (per project)    │
    └─────────────────┘  └──────────────────┘
```

## Tech Stack

| Layer          | Technology                           |
|----------------|--------------------------------------|
| Frontend       | Next.js 15, TailwindCSS, Monaco      |
| Backend        | Python 3.11+, FastAPI, SQLAlchemy    |
| Database       | PostgreSQL, Redis                    |
| AI             | OpenAI GPT-4 (multi-agent pipeline)  |
| Sandbox        | Docker containers                    |
| Deployment     | Vercel, Cloudflare, AWS              |

## Project Structure

```
ai-wrapper/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── agents/           # AI agent pipeline
│   │   │   ├── base.py       # Base OpenAI agent
│   │   │   ├── planner.py    # Prompt → specification
│   │   │   ├── architect.py  # Spec → file structure
│   │   │   ├── file_generator.py  # Generate file contents
│   │   │   ├── debug.py      # Auto-fix build errors
│   │   │   ├── improvement.py # Edit files via prompts
│   │   │   └── orchestrator.py # Pipeline coordinator
│   │   ├── api/              # REST API routes
│   │   │   ├── auth.py       # Authentication endpoints
│   │   │   └── projects.py   # Project CRUD + generation
│   │   ├── core/             # Configuration
│   │   │   ├── config.py     # Settings (env vars)
│   │   │   ├── database.py   # SQLAlchemy engine
│   │   │   └── security.py   # JWT + password hashing
│   │   ├── models/           # Database models
│   │   │   └── models.py     # User, Project, File, etc.
│   │   ├── schemas/          # Pydantic schemas
│   │   │   └── schemas.py    # Request/response models
│   │   ├── services/         # Business logic
│   │   │   ├── sandbox.py    # Docker container management
│   │   │   └── deployment.py # Cloud deployment
│   │   └── main.py           # FastAPI app entry point
│   ├── tests/                # Backend tests
│   ├── alembic/              # Database migrations
│   ├── pyproject.toml        # Python dependencies
│   └── Dockerfile
├── frontend/                 # Next.js frontend
│   ├── src/
│   │   ├── app/              # Next.js app router
│   │   │   ├── layout.tsx    # Root layout
│   │   │   ├── page.tsx      # Home/landing page
│   │   │   └── project/[id]/ # Project editor page
│   │   ├── components/       # React components
│   │   │   ├── PromptInput.tsx    # AI prompt input
│   │   │   ├── FileExplorer.tsx   # File tree browser
│   │   │   ├── CodeEditor.tsx     # Monaco editor wrapper
│   │   │   └── PreviewPanel.tsx   # Live preview iframe
│   │   ├── lib/              # Utilities
│   │   │   └── api.ts        # API client
│   │   └── styles/
│   │       └── globals.css   # TailwindCSS imports
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml        # Full stack orchestration
├── .env.example              # Environment template
└── .gitignore
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- OpenAI API key

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/azar99ahemad/ai-wrapper.git
cd ai-wrapper

# Copy environment file and set your API keys
cp .env.example .env

# Start all services
docker compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

**Backend:**
```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Path                                    | Description                    |
|--------|----------------------------------------|--------------------------------|
| POST   | `/api/auth/register`                   | Register a new user            |
| POST   | `/api/auth/login`                      | Login and get JWT token        |
| POST   | `/api/projects/generate`               | Generate project from prompt   |
| GET    | `/api/projects/{id}`                   | Get project details + files    |
| GET    | `/api/projects/{id}/files`             | List project files             |
| POST   | `/api/projects/{id}/files/{fid}/edit`  | Edit file with AI prompt       |
| POST   | `/api/projects/{id}/deploy`            | Deploy to cloud provider       |
| GET    | `/api/projects/{id}/preview-url`       | Get live preview URL           |

## AI Agent Pipeline

The system uses a multi-agent pipeline where each agent has a specific role:

1. **Planner Agent** – Converts user prompt into structured project specification (name, features, tech stack, pages)
2. **Architecture Agent** – Creates file map with dependency ordering
3. **File Generator Agent** – Generates each file with full content, respecting dependencies
4. **Debug Agent** – Automatically fixes compile/build errors
5. **Improvement Agent** – Updates files based on follow-up prompts

## Database Schema

- **users** – User accounts with plan type (free/pro/team)
- **projects** – Generated projects with status tracking
- **project_files** – Versioned file storage
- **ai_generations** – AI interaction logs with token usage
- **deployments** – Deployment records per provider
- **usage_limits** – Monthly generation tracking per user

## Billing Plans

| Plan | Generations/Month | Features                  |
|------|-------------------|---------------------------|
| Free | 10                | Basic generation           |
| Pro  | Unlimited         | All features               |
| Team | Unlimited         | Shared projects + collab   |

## Security

- Container isolation with resource limits (memory, CPU, timeout)
- JWT authentication with bcrypt password hashing
- CORS protection
- Sandboxed preview execution
- File access restrictions within containers