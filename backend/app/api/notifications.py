"""
Notifications API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    MarkAsReadRequest,
    NotificationStatsResponse
)
from app.services.notification import notification_service
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/notifications", tags=["notifications"])
security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Extract user ID from JWT token"""
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    return int(user_id)


@router.get("", response_model=NotificationListResponse)
def get_notifications(
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get user notifications

    - **limit**: Maximum number of notifications to return (1-100)
    - **unread_only**: Only return unread notifications
    """
    notifications = notification_service.get_user_notifications(
        db=db,
        user_id=user_id,
        limit=limit,
        unread_only=unread_only
    )

    total = len(notifications)
    unread_count = notification_service.get_unread_count(db=db, user_id=user_id)

    return NotificationListResponse(
        notifications=[NotificationResponse.from_orm(n) for n in notifications],
        total=total,
        unread_count=unread_count
    )


@router.get("/stats", response_model=NotificationStatsResponse)
def get_notification_stats(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get notification statistics
    """
    from app.models.notification import Notification

    total = db.query(Notification).filter(Notification.user_id == user_id).count()
    unread = notification_service.get_unread_count(db=db, user_id=user_id)

    # Count notifications from today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.sent_at >= today_start
    ).count()

    return NotificationStatsResponse(
        total_notifications=total,
        unread_count=unread,
        notifications_today=today_count
    )


@router.post("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Mark a specific notification as read
    """
    notification = notification_service.mark_as_read(
        db=db,
        notification_id=notification_id,
        user_id=user_id
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return {
        "status": "success",
        "message": "Notification marked as read",
        "notification_id": notification_id
    }


@router.post("/mark-all-read")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Mark all notifications as read for the current user
    """
    notification_service.mark_all_as_read(db=db, user_id=user_id)

    return {
        "status": "success",
        "message": "All notifications marked as read"
    }


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get a specific notification
    """
    from app.models.notification import Notification

    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return NotificationResponse.from_orm(notification)
