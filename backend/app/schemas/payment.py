"""
Payment Schemas
"""
from pydantic import BaseModel, EmailStr
from decimal import Decimal
from typing import Optional


class PaymentInitiate(BaseModel):
    """Schema for initiating a payment"""
    account_number: str
    amount: Decimal
    callback_url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "account_number": "0123456789",
                "amount": 5000.00,
                "callback_url": "http://localhost:3000/payment/callback"
            }
        }


class PaymentInitiateResponse(BaseModel):
    """Response after initiating payment"""
    success: bool
    authorization_url: str
    access_code: str
    reference: str
    amount: Decimal
    message: str


class PaymentVerify(BaseModel):
    """Schema for verifying payment"""
    reference: str


class PaymentVerifyResponse(BaseModel):
    """Response after verifying payment"""
    success: bool
    status: str  # success, failed, abandoned
    amount: Decimal
    reference: str
    message: str
    new_balance: Optional[Decimal] = None
