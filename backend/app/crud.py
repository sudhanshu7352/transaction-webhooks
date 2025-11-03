from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .models import Transaction, TransactionStatus
from datetime import datetime
from typing import Optional

def create_transaction_if_not_exists(db: Session, tx_data: dict) -> (Transaction, bool):
    """
    Create a transaction record if it does not exist.
    Returns (transaction_obj, created_flag)
    """
    # Check if exists
    stmt = select(Transaction).where(Transaction.transaction_id == tx_data["transaction_id"])
    res = db.execute(stmt).scalar_one_or_none()
    if res:
        return res, False

    tx = Transaction(
        transaction_id=tx_data["transaction_id"],
        source_account=tx_data["source_account"],
        destination_account=tx_data["destination_account"],
        amount=tx_data["amount"],
        currency=tx_data["currency"],
        status=TransactionStatus.PROCESSING,
    )
    db.add(tx)
    try:
        db.commit()
        db.refresh(tx)
        return tx, True
    except IntegrityError:
        db.rollback()
        # Another process inserted concurrently — fetch it
        res = db.execute(stmt).scalar_one()
        return res, False

def mark_transaction_processed(db: Session, transaction_id: str, processed_at: Optional[datetime]=None, status=TransactionStatus.PROCESSED):
    stmt = select(Transaction).where(Transaction.transaction_id == transaction_id)
    tx = db.execute(stmt).scalar_one_or_none()
    if not tx:
        return None
    tx.status = status
    tx.processed_at = processed_at or datetime.utcnow()
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx

def get_transaction(db: Session, transaction_id: str):
    stmt = select(Transaction).where(Transaction.transaction_id == transaction_id)
    return db.execute(stmt).scalar_one_or_none()
