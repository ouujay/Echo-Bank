"""
Bank Recipient Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class BankRecipient(Base):
    """Saved beneficiary/recipient model"""

    __tablename__ = "bank_recipients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("bank_users.id", ondelete="CASCADE"), nullable=False)
    recipient_name = Column(String(255), nullable=False)
    account_number = Column(String(10), nullable=False)
    bank_name = Column(String(100), nullable=False)
    bank_code = Column(String(10), nullable=False)
    paystack_recipient_code = Column(String(100), nullable=True)
    is_favorite = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    last_transfer_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("BankUser", back_populates="recipients")
    transactions = relationship("BankTransaction", back_populates="recipient")

    def __repr__(self):
        return f"<BankRecipient {self.recipient_name} - {self.account_number}>"
