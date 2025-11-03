# Full Stack Developer Assessment — FastAPI backend + React frontend

## Overview
This repository implements a backend that receives transaction webhooks, acknowledges them quickly (202), schedules background processing (simulated external call 30s), stores results in a MySQL DB, ensures idempotency, and exposes a transaction status endpoint. The frontend is a React+TS dashboard resembling superbryn.com styles with editable chart values saved in Supabase.

## Backend
- Tech: FastAPI, Celery, Redis, SQLAlchemy, MySQL
- Endpoints:
  - GET /         => health check
  - POST /v1/webhooks/transactions => accepts webhook JSON (returns 202)
  - GET /v1/transactions/{transaction_id} => status

### Setup (local / testing)
1. Copy `backend/.env.example` -> `backend/.env` and fill:
   - `DATABASE_URL` (your cloud MySQL)
   - `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` (e.g., `redis://redis:6379/0`)
2. Start services:
cd backend
docker-compose up --build

3. Start a Celery worker (in another terminal within the backend container environment if needed):
celery -A app.tasks.celery worker --loglevel=info --pool=solo

4. Test:
- POST webhook:
  ```
  POST http://localhost:8000/v1/webhooks/transactions
  {
    "transaction_id":"txn_abc123def456",
    "source_account":"acc_user_789",
    "destination_account":"acc_merchant_456",
    "amount":1500,
    "currency":"INR"
  }
  ```
- Immediately returns 202. After ~30s check:
  `GET http://localhost:8000/v1/transactions/txn_abc123def456`

## Frontend
- Tech: React + TypeScript, Recharts, Supabase (for persisting user values)
- Setup:
`cd frontend`

`npm install`

  `create .env`

VITE_SUPABASE_URL=...
VITE_SUPABASE_ANON_KEY=...
npm run dev


## Notes / Design choices
- Celery used for reliable background processing and retries; Redis is used as broker and result backend.
- Idempotency enforced using a database unique constraint on `transaction_id` and safe create-or-get semantics.
- Frontend saves user chart edits in Supabase keyed by email and chart_key; shows previous saved values and prompts overwrite.

## Replace placeholders
- Replace `.env` placeholders with your cloud MySQL connection string and Supabase keys.

