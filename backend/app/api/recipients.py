"""
Recipients API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.transfer import RecipientCreate, RecipientResponse
from app.services import recipient as recipient_service
from app.api.accounts import get_current_user_id
from typing import List

router = APIRouter(prefix="/recipients", tags=["Recipients"])


@router.get("", response_model=List[RecipientResponse])
def get_recipients(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get all saved recipients for the authenticated user
    """
    try:
        recipients = recipient_service.get_user_recipients(db, user_id)
        return recipients
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recipients: {str(e)}"
        )


@router.post("", response_model=RecipientResponse, status_code=status.HTTP_201_CREATED)
def create_recipient(
    recipient_data: RecipientCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Add a new recipient
    """
    try:
        recipient = recipient_service.create_recipient(db, user_id, recipient_data)
        return recipient
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create recipient: {str(e)}"
        )


@router.put("/{recipient_id}/favorite", response_model=RecipientResponse)
def toggle_favorite(
    recipient_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Toggle favorite status for a recipient
    """
    try:
        recipient = recipient_service.toggle_favorite(db, recipient_id, user_id)
        return recipient
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update recipient: {str(e)}"
        )


@router.delete("/{recipient_id}")
def delete_recipient(
    recipient_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Delete a recipient
    """
    try:
        result = recipient_service.delete_recipient(db, recipient_id, user_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete recipient: {str(e)}"
        )
