from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

from app.core.database import get_db
from app.services.transfers import transfer_service
from app.services.auth import auth_service
from app.models.transaction import Transaction
from app.models.user import User
from app.models.recipient import Recipient

router = APIRouter(prefix="/api/v1/transfers", tags=["transfers"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class InitiateTransferRequest(BaseModel):
    """Request body for initiating a transfer."""
    recipient_id: int = Field(..., description="ID of the recipient")
    amount: float = Field(..., gt=0, description="Amount to transfer (must be positive)")
    session_id: str = Field(..., description="Voice session ID")


class VerifyPinRequest(BaseModel):
    """Request body for PIN verification."""
    pin: str = Field(..., min_length=4, max_length=4, description="4-digit PIN")


class ConfirmTransferRequest(BaseModel):
    """Request body for confirming transfer."""
    confirmation: str = Field(default="confirm", description="Confirmation text")


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

@router.post("/initiate")
async def initiate_transfer(
    request: InitiateTransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initiate a new transfer.

    Validates:
    - Recipient exists
    - Sufficient balance
    - Within daily limit

    Returns transfer details with status "pending_pin".
    """
    # Get recipient
    recipient = db.query(Recipient).filter(
        Recipient.id == request.recipient_id
    ).first()

    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "RECIPIENT_NOT_FOUND",
                "message": "Recipient not found"
            }
        )

    amount = Decimal(str(request.amount))

    # Validate transfer (balance + daily limit)
    validation = await transfer_service.validate_transfer(current_user, amount, db)

    if not validation["valid"]:
        # Determine error type
        if not validation["balance_check"]["sufficient"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INSUFFICIENT_BALANCE",
                    "message": f"Your balance is ₦{validation['balance_check']['current_balance']:,.0f}. You cannot send ₦{amount:,.0f}.",
                    "current_balance": validation["balance_check"]["current_balance"],
                    "requested_amount": float(amount)
                }
            )

        if not validation["limit_check"]["within_limit"]:
            limit_info = validation["limit_check"]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "LIMIT_EXCEEDED",
                    "message": f"Your daily limit is ₦{limit_info['daily_limit']:,.0f}. You've used ₦{limit_info['used_amount']:,.0f}.",
                    "daily_limit": limit_info["daily_limit"],
                    "used_amount": limit_info["used_amount"],
                    "remaining": limit_info["remaining"],
                    "suggestion": f"Would you like to send ₦{limit_info['remaining']:,.0f} instead?"
                }
            )

    # Create transaction
    transaction = await transfer_service.create_transaction(
        sender=current_user,
        recipient=recipient,
        amount=amount,
        session_id=request.session_id,
        db=db
    )

    new_balance = float(current_user.balance - amount)

    return {
        "success": True,
        "data": {
            "transfer_id": transaction.transaction_ref,
            "status": "pending_pin",
            "recipient": {
                "name": recipient.name,
                "account_number": recipient.account_number,
                "bank_name": recipient.bank_name
            },
            "amount": float(amount),
            "currency": "NGN",
            "current_balance": float(current_user.balance),
            "new_balance": new_balance,
            "message": f"Sending ₦{amount:,.0f} to {recipient.name}. Please say your 4-digit PIN."
        }
    }


@router.post("/{transfer_id}/verify-pin")
async def verify_pin(
    transfer_id: str,
    request: VerifyPinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify PIN for a transfer.

    Tracks failed attempts and locks account after 3 failures.
    """
    # Get transaction
    transaction = await transfer_service.get_transaction_by_ref(transfer_id, db)

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    # Verify transaction belongs to current user
    if transaction.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to access this transaction"
        )

    # Check transaction status
    if transaction.status != "pending_pin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction is not awaiting PIN. Current status: {transaction.status}"
        )

    # TODO: Track attempts in session (for now using simple counter)
    # In production, get attempt_count from session storage
    attempt_count = 1  # This should come from session

    # Verify PIN with attempt tracking
    verification = await auth_service.handle_pin_verification(
        user=current_user,
        entered_pin=request.pin,
        db=db,
        attempt_count=attempt_count
    )

    # If locked, return 403
    if verification["locked"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "PIN_LOCKED",
                "message": "Too many incorrect attempts. Locked for 30 minutes.",
                "locked_until": verification["locked_until"].isoformat()
            }
        )

    # If PIN incorrect, return 401
    if not verification["verified"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_PIN",
                "message": f"Incorrect PIN. You have {verification['attempts_remaining']} attempts remaining.",
                "attempts_remaining": verification["attempts_remaining"]
            }
        )

    # PIN correct - update transaction status
    await transfer_service.update_transaction_status(
        transaction=transaction,
        new_status="pending_confirmation",
        db=db
    )

    return {
        "success": True,
        "data": {
            "transfer_id": transfer_id,
            "status": "pending_confirmation",
            "pin_verified": True,
            "message": "PIN verified. Say 'confirm' to complete the transfer."
        }
    }


@router.post("/{transfer_id}/confirm")
async def confirm_transfer(
    transfer_id: str,
    request: ConfirmTransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Confirm and execute the transfer.

    This is where money actually moves.
    """
    # Get transaction
    transaction = await transfer_service.get_transaction_by_ref(transfer_id, db)

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    # Verify transaction belongs to current user
    if transaction.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to access this transaction"
        )

    # Check transaction status
    if transaction.status != "pending_confirmation":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction not ready for confirmation. Current status: {transaction.status}"
        )

    # Execute transfer
    result = await transfer_service.execute_transfer(transaction, db)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "TRANSFER_FAILED",
                "message": "Transfer failed due to a network error. Your money was not deducted.",
                "retry_available": True,
                "error": result["error"]
            }
        )

    # Success!
    recipient = transaction.recipient

    return {
        "success": True,
        "data": {
            "transfer_id": transfer_id,
            "status": "completed",
            "recipient": {
                "name": recipient.name,
                "account_number": recipient.account_number
            },
            "amount": float(transaction.amount),
            "transaction_ref": transaction.transaction_ref,
            "timestamp": transaction.completed_at.isoformat(),
            "new_balance": result["new_balance"],
            "message": f"✅ Transfer successful! ₦{transaction.amount:,.0f} sent to {recipient.name}. New balance: ₦{result['new_balance']:,.0f}."
        }
    }


@router.post("/{transfer_id}/cancel")
async def cancel_transfer(
    transfer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a pending transfer.

    Can only cancel if not yet completed.
    """
    # Get transaction
    transaction = await transfer_service.get_transaction_by_ref(transfer_id, db)

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    # Verify transaction belongs to current user
    if transaction.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to access this transaction"
        )

    # Cancel transaction
    result = await transfer_service.cancel_transaction(transaction, db)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

    return {
        "success": True,
        "data": {
            "transfer_id": transfer_id,
            "status": "cancelled",
            "message": "Transfer cancelled. No money was sent."
        }
    }


@router.get("/{transfer_id}")
async def get_transfer(
    transfer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get transfer details by ID.
    """
    transaction = await transfer_service.get_transaction_by_ref(transfer_id, db)

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    # Verify transaction belongs to current user
    if transaction.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to access this transaction"
        )

    recipient = transaction.recipient

    return {
        "success": True,
        "data": {
            "transfer_id": transaction.transaction_ref,
            "status": transaction.status,
            "recipient": {
                "name": recipient.name,
                "account_number": recipient.account_number,
                "bank_name": recipient.bank_name
            },
            "amount": float(transaction.amount),
            "currency": transaction.currency,
            "created_at": transaction.created_at.isoformat(),
            "completed_at": transaction.completed_at.isoformat() if transaction.completed_at else None
        }
    }
