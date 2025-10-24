from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    """
    User model representing bank account holders.

    Attributes:
        id: Primary key
        account_number: Unique 10-digit account number
        full_name: User's full name
        email: User's email address (unique)
        phone: User's phone number
        pin_hash: Hashed PIN for transaction authorization
        balance: Current account balance in NGN
        daily_limit: Maximum daily transfer limit (default: ₦50,000)
        is_active: Account active status
        pin_locked_until: Timestamp until which PIN is locked (after failed attempts)
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(10), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(20))
    pin_hash = Column(String(255), nullable=False)
    balance = Column(Numeric(15, 2), default=0.00)
    daily_limit = Column(Numeric(15, 2), default=50000.00)
    is_active = Column(Boolean, default=True)
    pin_locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    recipients = relationship("Recipient", back_populates="user", cascade="all, delete-orphan")
    sent_transactions = relationship("Transaction", foreign_keys="Transaction.sender_id", back_populates="sender")

    def __repr__(self):
        return f"<User(id={self.id}, account_number='{self.account_number}', name='{self.full_name}')>"
