"""
Authentication Service
"""
from sqlalchemy.orm import Session
from app.models.user import BankUser
from app.models.account import BankAccount
from app.core.security import hash_password, verify_password, hash_pin, verify_pin, create_access_token
from app.schemas.auth import UserRegister, TokenResponse, PINVerificationResponse
from datetime import timedelta, datetime
from app.core.config import settings
from typing import Optional
import random


def generate_account_number() -> str:
    """Generate a random 10-digit account number"""
    return ''.join([str(random.randint(0, 9)) for _ in range(10)])


def register_user(db: Session, user_data: UserRegister) -> TokenResponse:
    """
    Register a new user and create their first account
    """
    # Check if user already exists
    existing_user = db.query(BankUser).filter(
        (BankUser.email == user_data.email) | (BankUser.phone == user_data.phone)
    ).first()

    if existing_user:
        raise ValueError("User with this email or phone already exists")

    # Hash password and PIN
    password_hashed = hash_password(user_data.password)
    pin_hashed = hash_pin(user_data.pin)

    # Create user
    new_user = BankUser(
        email=user_data.email,
        phone=user_data.phone,
        full_name=user_data.full_name,
        bvn=user_data.bvn,
        password_hash=password_hashed,
        pin_hash=pin_hashed,
        is_verified=True  # Auto-verify for demo
    )

    db.add(new_user)
    db.flush()  # Get user ID

    # Create first account (savings)
    account_number = generate_account_number()

    # Ensure unique account number
    while db.query(BankAccount).filter(BankAccount.account_number == account_number).first():
        account_number = generate_account_number()

    new_account = BankAccount(
        user_id=new_user.id,
        account_number=account_number,
        account_name=user_data.full_name,
        account_type='savings',
        balance=100000.00  # Starting balance for demo
    )

    db.add(new_account)
    db.commit()
    db.refresh(new_user)

    # Send welcome notification
    try:
        from app.services.notification import notification_service
        notification_service.send_welcome_notification(
            db=db,
            user_id=new_user.id,
            account_number=account_number
        )
    except Exception as e:
        # Don't fail registration if notification fails
        print(f"Failed to send welcome notification: {e}")

    # Create access token
    access_token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name
    )


def login_user(db: Session, email: str, password: str) -> TokenResponse:
    """
    Authenticate user and return access token
    """
    user = db.query(BankUser).filter(BankUser.email == email).first()

    if not user:
        raise ValueError("Invalid email or password")

    if not verify_password(password, user.password_hash):
        raise ValueError("Invalid email or password")

    if not user.is_active:
        raise ValueError("Account is deactivated")

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name
    )


def verify_pin_for_account(db: Session, account_number: str, pin: str) -> PINVerificationResponse:
    """
    Verify PIN for an account number
    """
    account = db.query(BankAccount).filter(BankAccount.account_number == account_number).first()

    if not account:
        return PINVerificationResponse(
            verified=False,
            error="Account not found"
        )

    user = db.query(BankUser).filter(BankUser.id == account.user_id).first()

    if not user:
        return PINVerificationResponse(
            verified=False,
            error="User not found"
        )

    # Check if PIN is locked
    if user.pin_locked_until and user.pin_locked_until > datetime.now():
        return PINVerificationResponse(
            verified=False,
            error=f"PIN locked until {user.pin_locked_until.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    # Verify PIN
    if not verify_pin(pin, user.pin_hash):
        # Increment failed attempts
        user.pin_attempts += 1

        if user.pin_attempts >= 3:
            # Lock PIN for 30 minutes
            from datetime import datetime, timedelta
            user.pin_locked_until = datetime.now() + timedelta(minutes=30)
            db.commit()
            return PINVerificationResponse(
                verified=False,
                error="PIN locked for 30 minutes due to multiple failed attempts"
            )

        db.commit()
        return PINVerificationResponse(
            verified=False,
            error=f"Invalid PIN. {3 - user.pin_attempts} attempts remaining"
        )

    # Reset attempts on successful verification
    user.pin_attempts = 0
    user.pin_locked_until = None
    db.commit()

    return PINVerificationResponse(
        verified=True,
        user_id=user.id,
        account_id=account.id,
        account_name=account.account_name,
        error=None
    )


def get_current_user(db: Session, user_id: int) -> Optional[BankUser]:
    """Get user by ID"""
    return db.query(BankUser).filter(BankUser.id == user_id).first()
