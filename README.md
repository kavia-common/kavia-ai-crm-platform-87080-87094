# kavia-ai-crm-platform-87080-87094

## CRM Backend (FastAPI) - Database Setup

1) Copy env:
- cp crm_backend/.env.example crm_backend/.env
- Edit DATABASE_URL to your DB (PostgreSQL recommended).
- For quick local dev you may use SQLite:
  DATABASE_URL=sqlite:///./crm_dev.db

2) Install dependencies:
- pip install -r crm_backend/requirements.txt

3) Run backend (dev):
- cd crm_backend
- uvicorn src.api.main:app --reload --port 3001

Tables are auto-created in development (APP_ENV=development).