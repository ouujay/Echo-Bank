"""
Notification Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificationResponse(BaseModel):
    """Notification response schema"""
    id: int
    notification_type: str
    channel: str
    title: str
    message: str
    transaction_ref: Optional[str] = None
    amount: Optional[str] = None
    recipient_name: Optional[str] = None
    is_read: bool
    sent_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """List of notifications with metadata"""
    notifications: list[NotificationResponse]
    total: int
    unread_count: int


class MarkAsReadRequest(BaseModel):
    """Mark notification as read request"""
    notification_id: int


class NotificationStatsResponse(BaseModel):
    """Notification statistics"""
    total_notifications: int
    unread_count: int
    notifications_today: int
