"""
Bank User Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class BankUser(Base):
    """Bank user/customer model"""

    __tablename__ = "bank_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    bvn = Column(String(11), nullable=True)  # Bank Verification Number
    password_hash = Column(String(255), nullable=False)
    pin_hash = Column(String(255), nullable=False)  # 4-digit transaction PIN
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    pin_attempts = Column(Integer, default=0)
    pin_locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    accounts = relationship("BankAccount", back_populates="user", cascade="all, delete-orphan")
    recipients = relationship("BankRecipient", back_populates="user", cascade="all, delete-orphan")
    auth_tokens = relationship("AuthToken", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BankUser {self.email}>"
