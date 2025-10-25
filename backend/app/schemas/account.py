"""
Account Schemas
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


class AccountBase(BaseModel):
    """Base account schema"""
    account_number: str
    account_name: str
    account_type: str
    balance: Decimal
    currency: str


class AccountResponse(AccountBase):
    """Account response schema"""
    id: int
    user_id: int
    daily_transfer_limit: Decimal
    monthly_transfer_limit: Decimal
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BalanceResponse(BaseModel):
    """Balance response schema"""
    account_number: str
    account_name: str
    balance: Decimal
    available_balance: Decimal
    currency: str

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    """Transaction response schema"""
    id: int
    transaction_ref: str
    transaction_type: str
    amount: Decimal
    fee: Decimal
    currency: str
    recipient_name: Optional[str] = None
    recipient_account: Optional[str] = None
    recipient_bank_name: Optional[str] = None
    status: str
    narration: Optional[str] = None
    initiated_via: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TransactionHistoryResponse(BaseModel):
    """Transaction history response with pagination"""
    transactions: List[TransactionResponse]
    total: int
    page: int
    page_size: int
