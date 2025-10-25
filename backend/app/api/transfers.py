"""
Transfers API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.transfer import (
    TransferInitiate,
    TransferPINVerify,
    TransferConfirm,
    TransferResponse
)
from app.services import transfer as transfer_service
from app.api.accounts import get_current_user_id

router = APIRouter(prefix="/transfers", tags=["Transfers"])


@router.post("/initiate", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
def initiate_transfer(
    transfer_data: TransferInitiate,
    db: Session = Depends(get_db)
):
    """
    Initiate a new transfer

    Creates a pending transaction requiring PIN verification.
    Can be called from app or EchoBank voice interface.
    """
    try:
        transfer_response = transfer_service.initiate_transfer(db, transfer_data)
        return transfer_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transfer initiation failed: {str(e)}"
        )


@router.post("/{transaction_id}/verify-pin", response_model=TransferResponse)
def verify_pin(
    transaction_id: int,
    pin_data: TransferPINVerify,
    db: Session = Depends(get_db)
):
    """
    Verify PIN for a pending transfer

    After successful PIN verification, transfer moves to pending_confirmation status.
    """
    if pin_data.transaction_id != transaction_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction ID mismatch"
        )

    try:
        # Get the account number from the transaction
        from app.models.transaction import BankTransaction
        from app.models.account import BankAccount

        transaction = db.query(BankTransaction).filter(BankTransaction.id == transaction_id).first()
        if not transaction:
            raise ValueError("Transaction not found")

        account = db.query(BankAccount).filter(BankAccount.id == transaction.account_id).first()
        if not account:
            raise ValueError("Account not found")

        transfer_response = transfer_service.verify_transfer_pin(
            db,
            transaction_id,
            pin_data.pin,
            account.account_number
        )
        return transfer_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PIN verification failed: {str(e)}"
        )


@router.post("/{transaction_id}/confirm", response_model=TransferResponse)
def confirm_transfer(
    transaction_id: int,
    confirm_data: TransferConfirm,
    db: Session = Depends(get_db)
):
    """
    Confirm and execute a transfer

    Executes the transfer by debiting the sender's account.
    In production, this will initiate a Paystack transfer.
    """
    if confirm_data.transaction_id != transaction_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction ID mismatch"
        )

    try:
        transfer_response = transfer_service.confirm_transfer(db, transaction_id)
        return transfer_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transfer confirmation failed: {str(e)}"
        )


@router.get("/{transaction_id}", response_model=TransferResponse)
def get_transfer(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """
    Get transfer status by transaction ID
    """
    try:
        transfer_response = transfer_service.get_transfer_status(db, transaction_id)
        return transfer_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve transfer: {str(e)}"
        )


@router.post("/{transaction_id}/cancel")
def cancel_transfer(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """
    Cancel a pending transfer
    """
    try:
        result = transfer_service.cancel_transfer(db, transaction_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel transfer: {str(e)}"
        )
