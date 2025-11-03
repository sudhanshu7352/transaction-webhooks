from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, func, UniqueConstraint
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from .database import Base
import enum

class TransactionStatus(str, enum.Enum):
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(128), nullable=False, unique=True, index=True)
    source_account = Column(String(128), nullable=False)
    destination_account = Column(String(128), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PROCESSING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    # store any extra metadata
    meta_data = Column(JSON, nullable=True)
