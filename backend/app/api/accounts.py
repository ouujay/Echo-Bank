"""
Accounts API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.account import AccountResponse, BalanceResponse, TransactionHistoryResponse
from app.services import account as account_service
from app.core.security import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List

router = APIRouter(prefix="/accounts", tags=["Accounts"])
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


@router.get("", response_model=List[AccountResponse])
def get_accounts(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get all accounts for the authenticated user
    """
    try:
        accounts = account_service.get_user_accounts(db, user_id)
        return accounts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve accounts: {str(e)}"
        )


@router.get("/{account_id}/balance", response_model=BalanceResponse)
def get_balance(
    account_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get balance for a specific account
    """
    try:
        # TODO: Verify that account belongs to user
        balance = account_service.get_account_balance(db, account_id)
        return balance
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve balance: {str(e)}"
        )


@router.get("/balance/{account_number}", response_model=BalanceResponse)
def get_balance_by_number(
    account_number: str,
    db: Session = Depends(get_db)
):
    """
    Get balance by account number (for EchoBank integration)
    No authentication required for demo purposes
    """
    try:
        balance = account_service.get_account_balance_by_number(db, account_number)
        return balance
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve balance: {str(e)}"
        )


@router.get("/{account_id}/transactions", response_model=TransactionHistoryResponse)
def get_transactions(
    account_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get transaction history for an account
    """
    try:
        # TODO: Verify that account belongs to user
        transactions = account_service.get_account_transactions(db, account_id, page, page_size)
        return transactions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve transactions: {str(e)}"
        )
