"""
Notification Model - Store all user notifications
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class NotificationType(str, enum.Enum):
    """Notification types"""
    CREDIT = "credit"
    DEBIT = "debit"
    TRANSFER_SENT = "transfer_sent"
    TRANSFER_RECEIVED = "transfer_received"
    LOGIN = "login"
    WELCOME = "welcome"
    LOW_BALANCE = "low_balance"
    PIN_CHANGE = "pin_change"
    ACCOUNT_UPDATE = "account_update"
    SECURITY_ALERT = "security_alert"


class NotificationChannel(str, enum.Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class Notification(Base):
    """User notifications table"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("bank_users.id"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=True, index=True)

    # Notification details
    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    channel = Column(SQLEnum(NotificationChannel), default=NotificationChannel.IN_APP)

    # Content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Metadata
    transaction_ref = Column(String(100), nullable=True)
    amount = Column(String(50), nullable=True)
    recipient_name = Column(String(255), nullable=True)

    # Status
    is_read = Column(Boolean, default=False)
    sent_at = Column(DateTime, default=datetime.now, nullable=False)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("BankUser", back_populates="notifications")
    account = relationship("BankAccount")
