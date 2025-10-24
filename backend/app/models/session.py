from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Session(Base):
    """
    Session model for tracking voice conversation sessions.

    Attributes:
        id: Primary key
        session_id: Unique session identifier (e.g., sess_abc123)
        user_id: Foreign key to user
        context: JSON field storing conversation context
        current_step: Current step in conversation flow
        created_at: Session creation time
        expires_at: Session expiration time
        is_active: Whether session is still active
    """
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    context = Column(JSON)
    current_step = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Session(session_id='{self.session_id}', step='{self.current_step}')>"
