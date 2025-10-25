"""
Transfer Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime


class TransferInitiate(BaseModel):
    """Schema for initiating a transfer"""
    account_number: str = Field(..., min_length=10, max_length=10)
    recipient_id: Optional[int] = None  # If saved recipient
    recipient_account: Optional[str] = Field(None, min_length=10, max_length=10)
    recipient_name: Optional[str] = None
    recipient_bank_code: Optional[str] = None
    recipient_bank_name: Optional[str] = None
    amount: Decimal = Field(..., gt=0)
    narration: Optional[str] = Field(None, max_length=500)
    session_id: Optional[str] = None  # For voice sessions
    initiated_via: str = "app"  # app, voice, web, ussd


class TransferPINVerify(BaseModel):
    """Schema for PIN verification during transfer"""
    transaction_id: int
    pin: str = Field(..., min_length=4, max_length=4)


class TransferConfirm(BaseModel):
    """Schema for confirming a transfer"""
    transaction_id: int


class TransferResponse(BaseModel):
    """Transfer response schema"""
    transaction_id: int
    transaction_ref: str
    amount: Decimal
    fee: Decimal
    total_amount: Decimal
    recipient_name: str
    recipient_account: str
    recipient_bank_name: str
    status: str
    message: str
    requires_pin: bool = False
    requires_confirmation: bool = False

    class Config:
        from_attributes = True


class RecipientCreate(BaseModel):
    """Schema for creating a recipient"""
    recipient_name: str = Field(..., min_length=2, max_length=255)
    account_number: str = Field(..., min_length=10, max_length=10)
    bank_name: str = Field(..., min_length=2, max_length=100)
    bank_code: str = Field(..., min_length=3, max_length=10)
    is_favorite: bool = False


class RecipientResponse(BaseModel):
    """Recipient response schema"""
    id: int
    recipient_name: str
    account_number: str
    bank_name: str
    bank_code: str
    is_favorite: bool
    is_verified: bool
    last_transfer_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AccountVerify(BaseModel):
    """Schema for account verification (Paystack name enquiry)"""
    account_number: str = Field(..., min_length=10, max_length=10)
    bank_code: str = Field(..., min_length=3, max_length=10)


class AccountVerifyResponse(BaseModel):
    """Account verification response"""
    verified: bool
    account_number: str
    account_name: Optional[str] = None
    bank_code: Optional[str] = None
    error: Optional[str] = None
