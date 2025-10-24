from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_ref = Column(String(50), unique=True, nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("recipients.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="NGN")
    status = Column(String(20), default="pending")
    # Status: pending, pending_pin, pending_confirmation, completed, failed, cancelled
    session_id = Column(String(100))
    paystack_transfer_code = Column(String(100))
    failure_reason = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_transactions")
    recipient = relationship("Recipient", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.transaction_ref} - {self.status}>"
