"""
Paystack Transfer and Daily Limit Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Boolean, Date, Text, func, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class PaystackTransfer(Base):
    """Paystack transfer tracking for reconciliation"""

    __tablename__ = "paystack_transfers"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("bank_transactions.id"), nullable=False)
    transfer_code = Column(String(100), unique=True, nullable=False, index=True)
    transfer_id = Column(String(100), nullable=True)
    recipient_code = Column(String(100), nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="NGN")
    status = Column(String(50), nullable=True)  # pending, success, failed, reversed
    reason = Column(Text, nullable=True)

    # Paystack response data
    paystack_response = Column(JSON, nullable=True)

    # Webhook tracking
    webhook_received = Column(Boolean, default=False)
    webhook_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    transaction = relationship("BankTransaction", back_populates="paystack_transfer")

    def __repr__(self):
        return f"<PaystackTransfer {self.transfer_code} - {self.status}>"


class DailyTransferLimit(Base):
    """Track daily transfer totals per account"""

    __tablename__ = "daily_transfer_limits"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=False)
    transfer_date = Column(Date, nullable=False)
    total_amount = Column(Numeric(15, 2), default=0.00)
    transfer_count = Column(Integer, default=0)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    account = relationship("BankAccount", back_populates="daily_limits")

    def __repr__(self):
        return f"<DailyTransferLimit Account:{self.account_id} Date:{self.transfer_date}>"
