"""
Mock Bank API Implementation

This is a demo implementation of the BankAPIClient interface.
It uses EchoBank's own database to simulate a real bank's API.

For Production:
    Banks should implement their own BankAPIClient that connects
    to their actual banking systems, databases, and payment processors.

Demo Purpose:
    - Shows how banks integrate with EchoBank
    - Provides working demo for hackathon
    - Reference implementation for real banks
"""

from app.integrations.bank_client import BankAPIClient, BankAPIError
from app.core.database import get_db
from app.models.user import User
from app.models.recipient import Recipient
from app.models.transaction import Transaction
from sqlalchemy.orm import Session
from typing import Dict, Optional
from decimal import Decimal
from datetime import datetime
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class MockBankAPI(BankAPIClient):
    """
    Mock implementation using EchoBank's demo database.

    Real banks would replace this with their actual API client.
    """

    def __init__(self):
        self.db: Session = next(get_db())

    async def verify_account(self, account_number: str, pin: str) -> Dict:
        """Verify account credentials"""
        try:
            user = self.db.query(User).filter(
                User.account_number == account_number,
                User.is_active == True
            ).first()

            if not user:
                return {
                    "verified": False,
                    "user_id": None,
                    "account_name": None,
                    "error": "Account not found"
                }

            if not pwd_context.verify(pin, user.pin_hash):
                return {
                    "verified": False,
                    "user_id": None,
                    "account_name": None,
                    "error": "Invalid PIN"
                }

            return {
                "verified": True,
                "user_id": str(user.id),
                "account_name": user.full_name,
                "error": None
            }

        except Exception as e:
            raise BankAPIError(f"Account verification failed: {str(e)}")

    async def get_balance(self, account_number: str, token: str) -> Dict:
        """Get account balance"""
        try:
            user = self.db.query(User).filter(
                User.account_number == account_number,
                User.is_active == True
            ).first()

            if not user:
                return {
                    "success": False,
                    "balance": Decimal("0"),
                    "currency": "NGN",
                    "available_balance": Decimal("0"),
                    "error": "Account not found"
                }

            return {
                "success": True,
                "balance": user.balance,
                "currency": "NGN",
                "available_balance": user.balance,  # Simplified - no holds
                "error": None
            }

        except Exception as e:
            raise BankAPIError(f"Failed to get balance: {str(e)}")

    async def get_recipients(
        self,
        account_number: str,
        token: str,
        favorites_only: bool = False
    ) -> Dict:
        """Get saved recipients"""
        try:
            user = self.db.query(User).filter(
                User.account_number == account_number
            ).first()

            if not user:
                return {
                    "success": False,
                    "recipients": [],
                    "error": "Account not found"
                }

            query = self.db.query(Recipient).filter(Recipient.user_id == user.id)

            if favorites_only:
                query = query.filter(Recipient.is_favorite == True)

            recipients = query.all()

            return {
                "success": True,
                "recipients": [
                    {
                        "id": str(r.id),
                        "name": r.name,
                        "account_number": r.account_number,
                        "bank_name": r.bank_name,
                        "bank_code": r.bank_code,
                        "is_favorite": r.is_favorite
                    }
                    for r in recipients
                ],
                "error": None
            }

        except Exception as e:
            raise BankAPIError(f"Failed to get recipients: {str(e)}")

    async def verify_recipient_account(
        self,
        account_number: str,
        bank_code: str,
        token: str
    ) -> Dict:
        """
        Verify recipient account (name enquiry)

        In production, this would call Paystack or bank's name enquiry service.
        For demo, we check if account exists in our database.
        """
        try:
            # Mock bank lookup - in production, call Paystack/bank API
            recipient_user = self.db.query(User).filter(
                User.account_number == account_number
            ).first()

            if recipient_user:
                return {
                    "success": True,
                    "account_name": recipient_user.full_name,
                    "account_number": account_number,
                    "bank_name": "Mock Bank",
                    "error": None
                }

            # For demo, return mock name for any account
            return {
                "success": True,
                "account_name": f"Account {account_number[-4:]}",
                "account_number": account_number,
                "bank_name": "External Bank",
                "error": None
            }

        except Exception as e:
            raise BankAPIError(f"Account verification failed: {str(e)}")

    async def initiate_transfer(
        self,
        sender_account: str,
        recipient_account: str,
        bank_code: str,
        amount: Decimal,
        narration: str,
        token: str
    ) -> Dict:
        """Initiate transfer (pending confirmation)"""
        try:
            sender = self.db.query(User).filter(
                User.account_number == sender_account
            ).first()

            if not sender:
                return {
                    "success": False,
                    "error": "Sender account not found"
                }

            # Check balance
            if sender.balance < amount:
                return {
                    "success": False,
                    "error": "Insufficient balance"
                }

            # Check daily limit
            today_total = self.db.query(Transaction).filter(
                Transaction.sender_id == sender.id,
                Transaction.status == "completed",
                Transaction.created_at >= datetime.utcnow().date()
            ).count()

            # Simplified - just check if amount exceeds limit
            if amount > sender.daily_limit:
                return {
                    "success": False,
                    "error": f"Amount exceeds daily limit of ₦{sender.daily_limit:,.2f}"
                }

            # Get recipient details
            recipient_info = await self.verify_recipient_account(
                recipient_account, bank_code, token
            )

            # Create pending transaction
            transfer_id = str(uuid.uuid4())
            transaction = Transaction(
                transaction_ref=transfer_id,
                sender_id=sender.id,
                amount=amount,
                status="pending_pin",
                narration=narration or "Transfer",
                recipient_account=recipient_account,
                recipient_name=recipient_info.get("account_name", "Unknown"),
                bank_code=bank_code
            )

            self.db.add(transaction)
            self.db.commit()

            fee = Decimal("10.00")  # Fixed ₦10 fee for demo
            total = amount + fee

            return {
                "success": True,
                "transfer_id": transfer_id,
                "status": "pending_confirmation",
                "recipient_name": recipient_info.get("account_name"),
                "amount": amount,
                "fee": fee,
                "total": total,
                "error": None
            }

        except Exception as e:
            self.db.rollback()
            raise BankAPIError(f"Transfer initiation failed: {str(e)}")

    async def confirm_transfer(
        self,
        transfer_id: str,
        pin: str,
        token: str
    ) -> Dict:
        """Confirm and execute transfer"""
        try:
            transaction = self.db.query(Transaction).filter(
                Transaction.transaction_ref == transfer_id
            ).first()

            if not transaction:
                return {
                    "success": False,
                    "error": "Transfer not found"
                }

            if transaction.status == "completed":
                return {
                    "success": False,
                    "error": "Transfer already completed"
                }

            sender = self.db.query(User).filter(
                User.id == transaction.sender_id
            ).first()

            # Verify PIN
            if not pwd_context.verify(pin, sender.pin_hash):
                return {
                    "success": False,
                    "error": "Invalid PIN"
                }

            # Check balance again (double-check)
            if sender.balance < transaction.amount:
                return {
                    "success": False,
                    "error": "Insufficient balance"
                }

            # Execute transfer - deduct from sender
            sender.balance -= transaction.amount
            transaction.status = "completed"
            transaction.updated_at = datetime.utcnow()

            self.db.commit()

            return {
                "success": True,
                "transaction_ref": transfer_id,
                "status": "completed",
                "amount": transaction.amount,
                "new_balance": sender.balance,
                "timestamp": transaction.updated_at,
                "error": None
            }

        except Exception as e:
            self.db.rollback()
            raise BankAPIError(f"Transfer confirmation failed: {str(e)}")

    async def cancel_transfer(
        self,
        transfer_id: str,
        token: str
    ) -> Dict:
        """Cancel pending transfer"""
        try:
            transaction = self.db.query(Transaction).filter(
                Transaction.transaction_ref == transfer_id
            ).first()

            if not transaction:
                return {
                    "success": False,
                    "error": "Transfer not found"
                }

            if transaction.status == "completed":
                return {
                    "success": False,
                    "error": "Cannot cancel completed transfer"
                }

            transaction.status = "cancelled"
            transaction.updated_at = datetime.utcnow()
            self.db.commit()

            return {
                "success": True,
                "status": "cancelled",
                "error": None
            }

        except Exception as e:
            self.db.rollback()
            raise BankAPIError(f"Transfer cancellation failed: {str(e)}")

    async def add_recipient(
        self,
        account_number: str,
        recipient_name: str,
        recipient_account: str,
        bank_name: str,
        bank_code: str,
        token: str
    ) -> Dict:
        """Add new recipient"""
        try:
            user = self.db.query(User).filter(
                User.account_number == account_number
            ).first()

            if not user:
                return {
                    "success": False,
                    "error": "Account not found"
                }

            # Check if recipient already exists
            existing = self.db.query(Recipient).filter(
                Recipient.user_id == user.id,
                Recipient.account_number == recipient_account
            ).first()

            if existing:
                return {
                    "success": False,
                    "error": "Recipient already exists"
                }

            recipient = Recipient(
                user_id=user.id,
                name=recipient_name,
                account_number=recipient_account,
                bank_name=bank_name,
                bank_code=bank_code,
                is_favorite=False
            )

            self.db.add(recipient)
            self.db.commit()
            self.db.refresh(recipient)

            return {
                "success": True,
                "recipient_id": str(recipient.id),
                "recipient": {
                    "id": str(recipient.id),
                    "name": recipient.name,
                    "account_number": recipient.account_number,
                    "bank_name": recipient.bank_name,
                    "bank_code": recipient.bank_code
                },
                "error": None
            }

        except Exception as e:
            self.db.rollback()
            raise BankAPIError(f"Failed to add recipient: {str(e)}")

    async def get_transaction_history(
        self,
        account_number: str,
        token: str,
        limit: int = 10
    ) -> Dict:
        """Get recent transactions"""
        try:
            user = self.db.query(User).filter(
                User.account_number == account_number
            ).first()

            if not user:
                return {
                    "success": False,
                    "transactions": [],
                    "error": "Account not found"
                }

            transactions = self.db.query(Transaction).filter(
                Transaction.sender_id == user.id
            ).order_by(Transaction.created_at.desc()).limit(limit).all()

            return {
                "success": True,
                "transactions": [
                    {
                        "id": t.transaction_ref,
                        "type": "debit",
                        "amount": t.amount,
                        "balance_after": user.balance,  # Simplified
                        "description": t.narration,
                        "timestamp": t.created_at,
                        "status": t.status
                    }
                    for t in transactions
                ],
                "error": None
            }

        except Exception as e:
            raise BankAPIError(f"Failed to get transactions: {str(e)}")


# Singleton instance for demo
mock_bank_client = MockBankAPI()
