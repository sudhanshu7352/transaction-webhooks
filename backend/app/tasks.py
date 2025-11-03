from celery import Celery
import time
from datetime import datetime
from .config import settings
from .database import SessionLocal
from .crud import mark_transaction_processed
from .models import TransactionStatus

celery = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery.conf.worker_max_tasks_per_child = 100
celery.conf.task_acks_late = True
celery.conf.task_reject_on_worker_lost = True

@celery.task(bind=True, name="process_transaction_task")
def process_transaction_task(self, transaction_id: str):
    """
    Simulate processing that takes ~30 seconds (simulate external API call)
    and then mark transaction as PROCESSED. Retries on failure.
    """
    try:
        # simulate 30s external call
        time.sleep(30)
        db = SessionLocal()
        mark_transaction_processed(db, transaction_id, processed_at=datetime.utcnow(), status=TransactionStatus.PROCESSED)
        db.close()
        return {"status": "processed", "transaction_id": transaction_id}
    except Exception as exc:
        # Optionally mark as FAILED
        try:
            db = SessionLocal()
            mark_transaction_processed(db, transaction_id, processed_at=datetime.utcnow(), status=TransactionStatus.FAILED)
            db.close()
        except:
            pass
        raise self.retry(exc=exc, countdown=5, max_retries=3)
