"""
Authentication API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, PINVerification, PINVerificationResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user

    Creates a new user account and their first savings account with ₦100,000 starting balance
    """
    try:
        token_response = auth_service.register_user(db, user_data)
        return token_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login user

    Authenticates user and returns JWT access token
    """
    try:
        token_response = auth_service.login_user(db, login_data.email, login_data.password)
        return token_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/verify-pin", response_model=PINVerificationResponse)
def verify_pin(pin_data: PINVerification, db: Session = Depends(get_db)):
    """
    Verify transaction PIN

    Verifies the 4-digit PIN for an account number.
    Used by EchoBank and during transfer confirmation.
    """
    try:
        verification_response = auth_service.verify_pin_for_account(
            db,
            pin_data.account_number,
            pin_data.pin
        )

        if not verification_response.verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=verification_response.error or "PIN verification failed"
            )

        return verification_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PIN verification failed: {str(e)}"
        )


@router.post("/logout")
def logout():
    """
    Logout user

    In a production app, this would revoke the JWT token
    For now, it's handled client-side by deleting the token
    """
    return {"message": "Logged out successfully"}
