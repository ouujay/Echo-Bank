from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base


class Recipient(Base):
    """
    Recipient model representing saved beneficiaries.

    Attributes:
        id: Primary key
        user_id: Foreign key to user who saved this recipient
        name: Recipient's name
        account_number: Recipient's 10-digit account number
        bank_name: Name of recipient's bank
        bank_code: Bank code (e.g., "057" for Zenith)
        is_favorite: Whether recipient is marked as favorite
        created_at: When recipient was added
    """
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    account_number = Column(String(10), nullable=False)
    bank_name = Column(String(100), nullable=False)
    bank_code = Column(String(10), nullable=False)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="recipients")
    transactions = relationship("Transaction", back_populates="recipient")

    def __repr__(self):
        return f"<Recipient {self.name} - {self.bank_name}>"
