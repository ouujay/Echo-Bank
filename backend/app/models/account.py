"""
Bank Account Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class BankAccount(Base):
    """Bank account model (savings, current)"""

    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("bank_users.id", ondelete="CASCADE"), nullable=False)
    account_number = Column(String(10), unique=True, nullable=False, index=True)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(20), default="savings")  # savings, current
    balance = Column(Numeric(15, 2), default=0.00)
    currency = Column(String(3), default="NGN")
    daily_transfer_limit = Column(Numeric(15, 2), default=50000.00)
    monthly_transfer_limit = Column(Numeric(15, 2), default=500000.00)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("BankUser", back_populates="accounts")
    transactions = relationship("BankTransaction", back_populates="account", cascade="all, delete-orphan")
    daily_limits = relationship("DailyTransferLimit", back_populates="account", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BankAccount {self.account_number} - {self.account_name}>"
