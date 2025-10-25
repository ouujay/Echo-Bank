"""
Payment API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.payment import (
    PaymentInitiate,
    PaymentInitiateResponse,
    PaymentVerify,
    PaymentVerifyResponse,
)
from app.services.payment import initiate_wallet_funding, verify_wallet_funding

router = APIRouter(prefix="/api/payments", tags=["payments"])
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


@router.post("/fund-wallet", response_model=PaymentInitiateResponse)
def fund_wallet(
    payment_data: PaymentInitiate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Initiate wallet funding via Paystack
    Returns authorization_url to redirect user for payment
    """
    try:
        result = initiate_wallet_funding(db, payment_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment initialization failed: {str(e)}")


@router.post("/verify", response_model=PaymentVerifyResponse)
def verify_payment(
    verify_data: PaymentVerify,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Verify payment and credit account if successful
    """
    try:
        result = verify_wallet_funding(db, verify_data.reference)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment verification failed: {str(e)}")


@router.get("/callback")
def payment_callback(reference: str, db: Session = Depends(get_db)):
    """
    Paystack payment callback endpoint
    This is where Paystack redirects after payment
    """
    # In a real app, you'd redirect to a frontend page
    # For now, just return a simple success page
    return {
        "status": "success",
        "message": "Payment completed. You can close this page.",
        "reference": reference
    }
