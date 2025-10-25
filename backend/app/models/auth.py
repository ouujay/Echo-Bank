"""
Authentication Token Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class AuthToken(Base):
    """JWT authentication token tracking"""

    __tablename__ = "auth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("bank_users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    device_id = Column(String(255), nullable=True)
    device_name = Column(String(255), nullable=True)
    ip_address = Column(String(50), nullable=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("BankUser", back_populates="auth_tokens")

    def __repr__(self):
        return f"<AuthToken User:{self.user_id} Expires:{self.expires_at}>"
