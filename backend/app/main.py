from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from .config import settings
from .database import init_db, SessionLocal
from .schemas import WebhookTransaction, TransactionResponse, HealthResponse
from .crud import create_transaction_if_not_exists, get_transaction
from .tasks import process_transaction_task
from sqlalchemy.orm import Session
import logging

app = FastAPI(title="Transaction Webhooks Service")

logger = logging.getLogger("uvicorn.error")

# initialize DB (create tables)
init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_model=HealthResponse)
def health_check():
    return {"status": "HEALTHY", "current_time": datetime.now(timezone.utc)}

@app.post("/v1/webhooks/transactions", status_code=status.HTTP_202_ACCEPTED)
def receive_webhook(payload: WebhookTransaction, db: Session = Depends(get_db)):
    """
    Accepts webhook and immediately returns 202. Background processing scheduled via Celery.
    Ensures idempotency by checking transaction_id uniqueness.
    """
    tx_data = payload.dict()
    # Try to create record, if it exists return 202 but do not requeue another processing
    tx, created = create_transaction_if_not_exists(db, tx_data)
    if created:
        # Schedule Celery background task
        # We don't wait for the Celery task — immediate ack is required
        process_transaction_task.delay(tx.transaction_id)
        logger.info(f"Scheduled processing for tx {tx.transaction_id}")
    else:
        logger.info(f"Transaction {tx.transaction_id} already exists - idempotent handling")
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={"ack": True})

@app.get("/v1/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction_status(transaction_id: str, db: Session = Depends(get_db)):
    tx = get_transaction(db, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {
        "transaction_id": tx.transaction_id,
        "source_account": tx.source_account,
        "destination_account": tx.destination_account,
        "amount": tx.amount,
        "currency": tx.currency,
        "status": tx.status.value,
        "created_at": tx.created_at,
        "processed_at": tx.processed_at,
    }
