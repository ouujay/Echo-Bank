"""
Bank API Client Interface

EchoBank is a voice intelligence API that integrates with existing bank systems.
Banks implement this interface to connect their APIs with EchoBank's voice features.

Architecture:
    Bank Mobile App → EchoBank Voice API → Bank's Backend API

Integration Flow:
    1. User speaks in bank's app
    2. Bank sends audio to EchoBank /transcribe
    3. EchoBank returns intent and entities
    4. Bank executes action using their own API
    5. Bank sends result to EchoBank for voice response
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime


class BankAPIClient(ABC):
    """
    Abstract interface for bank API integration.

    Banks must implement this interface to connect their backend
    with EchoBank's voice intelligence features.
    """

    @abstractmethod
    async def verify_account(self, account_number: str, pin: str) -> Dict:
        """
        Verify account credentials

        Args:
            account_number: Customer account number
            pin: Customer PIN/password

        Returns:
            {
                "verified": bool,
                "user_id": str,
                "account_name": str,
                "error": Optional[str]
            }
        """
        pass

    @abstractmethod
    async def get_balance(self, account_number: str, token: str) -> Dict:
        """
        Get account balance

        Args:
            account_number: Customer account number
            token: Authentication token from bank

        Returns:
            {
                "success": bool,
                "balance": Decimal,
                "currency": str,
                "available_balance": Decimal,
                "error": Optional[str]
            }
        """
        pass

    @abstractmethod
    async def get_recipients(
        self,
        account_number: str,
        token: str,
        favorites_only: bool = False
    ) -> Dict:
        """
        Get saved recipients/beneficiaries

        Args:
            account_number: Customer account number
            token: Authentication token
            favorites_only: Return only favorite recipients

        Returns:
            {
                "success": bool,
                "recipients": [
                    {
                        "id": str,
                        "name": str,
                        "account_number": str,
                        "bank_name": str,
                        "bank_code": str,
                        "is_favorite": bool
                    }
                ],
                "error": Optional[str]
            }
        """
        pass

    @abstractmethod
    async def verify_recipient_account(
        self,
        account_number: str,
        bank_code: str,
        token: str
    ) -> Dict:
        """
        Verify recipient account exists (name enquiry)

        Args:
            account_number: Recipient account number
            bank_code: Bank code (e.g., "058" for GTBank)
            token: Authentication token

        Returns:
            {
                "success": bool,
                "account_name": str,
                "account_number": str,
                "bank_name": str,
                "error": Optional[str]
            }
        """
        pass

    @abstractmethod
    async def initiate_transfer(
        self,
        sender_account: str,
        recipient_account: str,
        bank_code: str,
        amount: Decimal,
        narration: str,
        token: str
    ) -> Dict:
        """
        Initiate money transfer (requires confirmation)

        Args:
            sender_account: Sender account number
            recipient_account: Recipient account number
            bank_code: Recipient bank code
            amount: Transfer amount
            narration: Transfer description
            token: Authentication token

        Returns:
            {
                "success": bool,
                "transfer_id": str,
                "status": str,  # "pending_confirmation"
                "recipient_name": str,
                "amount": Decimal,
                "fee": Decimal,
                "total": Decimal,
                "error": Optional[str]
            }
        """
        pass

    @abstractmethod
    async def confirm_transfer(
        self,
        transfer_id: str,
        pin: str,
        token: str
    ) -> Dict:
        """
        Confirm and execute transfer with PIN

        Args:
            transfer_id: Transfer ID from initiate_transfer
            pin: Customer PIN for authorization
            token: Authentication token

        Returns:
            {
                "success": bool,
                "transaction_ref": str,
                "status": str,  # "completed" or "failed"
                "amount": Decimal,
                "new_balance": Decimal,
                "timestamp": datetime,
                "error": Optional[str]
            }
        """
        pass

    @abstractmethod
    async def cancel_transfer(
        self,
        transfer_id: str,
        token: str
    ) -> Dict:
        """
        Cancel pending transfer

        Args:
            transfer_id: Transfer ID to cancel
            token: Authentication token

        Returns:
            {
                "success": bool,
                "status": str,  # "cancelled"
                "error": Optional[str]
            }
        """
        pass

    @abstractmethod
    async def add_recipient(
        self,
        account_number: str,
        recipient_name: str,
        recipient_account: str,
        bank_name: str,
        bank_code: str,
        token: str
    ) -> Dict:
        """
        Add new recipient/beneficiary

        Args:
            account_number: Customer account number
            recipient_name: Name of recipient
            recipient_account: Recipient account number
            bank_name: Recipient bank name
            bank_code: Recipient bank code
            token: Authentication token

        Returns:
            {
                "success": bool,
                "recipient_id": str,
                "recipient": {
                    "id": str,
                    "name": str,
                    "account_number": str,
                    "bank_name": str,
                    "bank_code": str
                },
                "error": Optional[str]
            }
        """
        pass

    @abstractmethod
    async def get_transaction_history(
        self,
        account_number: str,
        token: str,
        limit: int = 10
    ) -> Dict:
        """
        Get recent transactions

        Args:
            account_number: Customer account number
            token: Authentication token
            limit: Number of transactions to return

        Returns:
            {
                "success": bool,
                "transactions": [
                    {
                        "id": str,
                        "type": str,  # "debit" or "credit"
                        "amount": Decimal,
                        "balance_after": Decimal,
                        "description": str,
                        "timestamp": datetime,
                        "status": str
                    }
                ],
                "error": Optional[str]
            }
        """
        pass


class BankAPIError(Exception):
    """Exception raised when bank API call fails"""

    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
