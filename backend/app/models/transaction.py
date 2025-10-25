"""
Bank Transaction Model
"""
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class BankTransaction(Base):
    """Bank transaction model for all transfers and transactions"""

    __tablename__ = "bank_transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=False)
    transaction_ref = Column(String(50), unique=True, nullable=False, index=True)
    transaction_type = Column(String(20), nullable=False)  # debit, credit, transfer
    amount = Column(Numeric(15, 2), nullable=False)
    fee = Column(Numeric(10, 2), default=0.00)
    currency = Column(String(3), default="NGN")

    # For transfers
    recipient_id = Column(Integer, ForeignKey("bank_recipients.id"), nullable=True)
    recipient_account = Column(String(10), nullable=True)
    recipient_name = Column(String(255), nullable=True)
    recipient_bank_name = Column(String(100), nullable=True)
    recipient_bank_code = Column(String(10), nullable=True)

    # Status tracking
    status = Column(String(20), default="pending")  # pending_pin, pending_confirmation, processing, completed, failed, cancelled
    narration = Column(Text, nullable=True)

    # Paystack integration
    paystack_transfer_code = Column(String(100), nullable=True, index=True)
    paystack_transfer_id = Column(String(100), nullable=True)
    paystack_status = Column(String(50), nullable=True)

    # Timestamps
    initiated_at = Column(DateTime, server_default=func.now())
    confirmed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)

    # Failure tracking
    failure_reason = Column(Text, nullable=True)

    # Voice/session tracking
    session_id = Column(String(100), nullable=True)
    initiated_via = Column(String(20), default="app")  # app, voice, ussd, web

    created_at = Column(DateTime, server_default=func.now(), index=True)

    # Relationships
    account = relationship("BankAccount", back_populates="transactions")
    recipient = relationship("BankRecipient", back_populates="transactions")
    paystack_transfer = relationship("PaystackTransfer", back_populates="transaction", uselist=False)

    def __repr__(self):
        return f"<BankTransaction {self.transaction_ref} - {self.status}>"
