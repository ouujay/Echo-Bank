from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional

from app.core.database import get_db
from app.models.recipient import Recipient
from app.models.user import User

router = APIRouter(prefix="/api/v1/recipients", tags=["recipients"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AddRecipientRequest(BaseModel):
    """Request body for adding a new recipient."""
    name: str = Field(..., min_length=1, max_length=255, description="Recipient's full name")
    account_number: str = Field(..., min_length=10, max_length=10, description="10-digit account number")
    bank_name: str = Field(..., min_length=1, max_length=100, description="Bank name")
    bank_code: str = Field(..., min_length=1, max_length=10, description="Bank code (e.g., 057)")
    is_favorite: bool = Field(default=False, description="Mark as favorite")


class RecipientResponse(BaseModel):
    """Response model for a single recipient."""
    id: int
    name: str
    account_number: str
    bank_name: str
    bank_code: str
    is_favorite: bool


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_current_user(db: Session = Depends(get_db)) -> User:
    """
    Get current authenticated user.
    TODO: Replace with actual JWT authentication.
    For now, returns a test user (id=1).
    """
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please create a test user first."
        )
    return user


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/search")
async def search_recipients(
    name: str = Query(..., min_length=1, description="Name to search for"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search for recipients by name.

    Returns:
    - Single match: One recipient found
    - Multiple matches: List of recipients with selection prompt
    - No match: 404 error with suggestion to add recipient
    """
    # Search in user's saved recipients (case-insensitive)
    recipients = db.query(Recipient).filter(
        Recipient.user_id == current_user.id,
        Recipient.name.ilike(f"%{name}%")
    ).limit(limit).all()

    # No recipients found
    if not recipients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "RECIPIENT_NOT_FOUND",
                "message": f"I couldn't find {name} in your contacts.",
                "suggestion": "Say 'add new' to add them."
            }
        )

    # Single match found
    if len(recipients) == 1:
        recipient = recipients[0]
        return {
            "success": True,
            "data": {
                "recipients": [{
                    "id": recipient.id,
                    "name": recipient.name,
                    "account_number": recipient.account_number,
                    "bank_name": recipient.bank_name,
                    "bank_code": recipient.bank_code
                }],
                "match_type": "single",
                "message": f"Found {recipient.name} at {recipient.bank_name}."
            }
        }

    # Multiple matches found
    recipient_list = []
    for i, r in enumerate(recipients, 1):
        recipient_list.append({
            "id": r.id,
            "name": r.name,
            "account_number": r.account_number,
            "bank_name": r.bank_name
        })

    # Create selection message
    if len(recipients) == 2:
        message = f"I found {len(recipients)} matches. Say 1 for {recipients[0].name} or 2 for {recipients[1].name}."
    else:
        message = f"I found {len(recipients)} matches. Say the number for your choice."

    return {
        "success": True,
        "data": {
            "recipients": recipient_list,
            "match_type": "multiple",
            "message": message
        }
    }


@router.post("")
async def add_recipient(
    request: AddRecipientRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a new recipient to user's saved beneficiaries.
    """
    # Check if recipient already exists for this user
    existing = db.query(Recipient).filter(
        Recipient.user_id == current_user.id,
        Recipient.account_number == request.account_number,
        Recipient.bank_code == request.bank_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "RECIPIENT_EXISTS",
                "message": f"{request.name} is already in your contacts.",
                "recipient_id": existing.id
            }
        )

    # Create new recipient
    new_recipient = Recipient(
        user_id=current_user.id,
        name=request.name,
        account_number=request.account_number,
        bank_name=request.bank_name,
        bank_code=request.bank_code,
        is_favorite=request.is_favorite
    )

    db.add(new_recipient)
    db.commit()
    db.refresh(new_recipient)

    return {
        "success": True,
        "data": {
            "recipient": {
                "id": new_recipient.id,
                "name": new_recipient.name,
                "account_number": new_recipient.account_number,
                "bank_name": new_recipient.bank_name,
                "bank_code": new_recipient.bank_code,
                "is_favorite": new_recipient.is_favorite
            },
            "message": f"✅ {new_recipient.name} added to your contacts."
        }
    }


@router.get("")
async def list_recipients(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    favorites_only: bool = Query(False, description="Show only favorites"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all recipients for the current user.

    Optional filters:
    - favorites_only: Show only favorite recipients
    """
    query = db.query(Recipient).filter(Recipient.user_id == current_user.id)

    if favorites_only:
        query = query.filter(Recipient.is_favorite == True)

    recipients = query.order_by(Recipient.is_favorite.desc(), Recipient.name).limit(limit).all()

    recipient_list = [
        {
            "id": r.id,
            "name": r.name,
            "account_number": r.account_number,
            "bank_name": r.bank_name,
            "bank_code": r.bank_code,
            "is_favorite": r.is_favorite
        }
        for r in recipients
    ]

    return {
        "success": True,
        "data": {
            "recipients": recipient_list,
            "count": len(recipient_list)
        }
    }


@router.get("/{recipient_id}")
async def get_recipient(
    recipient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific recipient by ID.
    """
    recipient = db.query(Recipient).filter(
        Recipient.id == recipient_id,
        Recipient.user_id == current_user.id
    ).first()

    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found"
        )

    return {
        "success": True,
        "data": {
            "recipient": {
                "id": recipient.id,
                "name": recipient.name,
                "account_number": recipient.account_number,
                "bank_name": recipient.bank_name,
                "bank_code": recipient.bank_code,
                "is_favorite": recipient.is_favorite,
                "created_at": recipient.created_at.isoformat()
            }
        }
    }


@router.delete("/{recipient_id}")
async def delete_recipient(
    recipient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a recipient from saved beneficiaries.
    """
    recipient = db.query(Recipient).filter(
        Recipient.id == recipient_id,
        Recipient.user_id == current_user.id
    ).first()

    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found"
        )

    name = recipient.name
    db.delete(recipient)
    db.commit()

    return {
        "success": True,
        "data": {
            "message": f"{name} removed from your contacts."
        }
    }


@router.patch("/{recipient_id}/favorite")
async def toggle_favorite(
    recipient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Toggle recipient favorite status.
    """
    recipient = db.query(Recipient).filter(
        Recipient.id == recipient_id,
        Recipient.user_id == current_user.id
    ).first()

    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found"
        )

    # Toggle favorite status
    recipient.is_favorite = not recipient.is_favorite
    db.commit()

    status_text = "added to favorites" if recipient.is_favorite else "removed from favorites"

    return {
        "success": True,
        "data": {
            "recipient_id": recipient.id,
            "is_favorite": recipient.is_favorite,
            "message": f"{recipient.name} {status_text}."
        }
    }
