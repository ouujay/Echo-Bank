"""
Paystack Integration Service
"""
import requests
from typing import Dict, Optional
from app.core.config import settings
from decimal import Decimal


class PaystackService:
    """Service for Paystack API integration"""

    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.base_url = settings.PAYSTACK_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    def verify_account(self, account_number: str, bank_code: str) -> Dict:
        """
        Verify account name via Paystack Name Enquiry

        Returns: {
            "success": bool,
            "account_number": str,
            "account_name": str,
            "bank_code": str
        }
        """
        try:
            url = f"{self.base_url}/bank/resolve"
            params = {
                "account_number": account_number,
                "bank_code": bank_code,
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            data = response.json()

            if response.status_code == 200 and data.get("status"):
                return {
                    "success": True,
                    "account_number": data["data"]["account_number"],
                    "account_name": data["data"]["account_name"],
                    "bank_code": bank_code,
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Account verification failed"),
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Verification failed: {str(e)}",
            }

    def create_transfer_recipient(
        self,
        recipient_name: str,
        account_number: str,
        bank_code: str,
        currency: str = "NGN",
    ) -> Dict:
        """
        Create a Paystack transfer recipient

        Returns: {
            "success": bool,
            "recipient_code": str,  # e.g., "RCP_xyz123"
            "recipient_id": int
        }
        """
        try:
            url = f"{self.base_url}/transferrecipient"
            payload = {
                "type": "nuban",
                "name": recipient_name,
                "account_number": account_number,
                "bank_code": bank_code,
                "currency": currency,
            }

            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            data = response.json()

            if response.status_code == 201 and data.get("status"):
                return {
                    "success": True,
                    "recipient_code": data["data"]["recipient_code"],
                    "recipient_id": data["data"]["id"],
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Failed to create recipient"),
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create recipient: {str(e)}",
            }

    def initiate_transfer(
        self,
        recipient_code: str,
        amount: Decimal,
        reason: str,
        reference: Optional[str] = None,
    ) -> Dict:
        """
        Initiate a Paystack transfer

        Args:
            recipient_code: Paystack recipient code (RCP_xxx)
            amount: Amount in Naira (will be converted to kobo)
            reason: Transfer description
            reference: Optional transaction reference

        Returns: {
            "success": bool,
            "transfer_code": str,  # e.g., "TRF_xyz"
            "transfer_id": int,
            "status": str,  # "pending", "success", "failed"
            "amount": Decimal
        }
        """
        try:
            url = f"{self.base_url}/transfer"

            # Convert amount to kobo (Paystack requires kobo)
            amount_in_kobo = int(amount * 100)

            payload = {
                "source": "balance",
                "amount": amount_in_kobo,
                "recipient": recipient_code,
                "reason": reason,
                "currency": "NGN",
            }

            if reference:
                payload["reference"] = reference

            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            data = response.json()

            if response.status_code == 200 and data.get("status"):
                return {
                    "success": True,
                    "transfer_code": data["data"]["transfer_code"],
                    "transfer_id": data["data"]["id"],
                    "status": data["data"]["status"],
                    "amount": amount,
                    "response": data["data"],
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Transfer failed"),
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Transfer initiation failed: {str(e)}",
            }

    def verify_transfer(self, transfer_code: str) -> Dict:
        """
        Verify transfer status

        Returns: {
            "success": bool,
            "status": str,  # "pending", "success", "failed", "reversed"
            "amount": Decimal,
            "reason": str
        }
        """
        try:
            url = f"{self.base_url}/transfer/verify/{transfer_code}"

            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()

            if response.status_code == 200 and data.get("status"):
                transfer_data = data["data"]
                return {
                    "success": True,
                    "status": transfer_data["status"],
                    "amount": Decimal(transfer_data["amount"]) / 100,  # Convert from kobo
                    "reason": transfer_data.get("reason", ""),
                    "response": transfer_data,
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Verification failed"),
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Transfer verification failed: {str(e)}",
            }

    def get_banks(self) -> Dict:
        """
        Get list of Nigerian banks from Paystack

        Returns: {
            "success": bool,
            "banks": [{"name": str, "code": str}]
        }
        """
        try:
            url = f"{self.base_url}/bank"
            params = {"currency": "NGN", "perPage": 100}

            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            data = response.json()

            if response.status_code == 200 and data.get("status"):
                banks = [
                    {"name": bank["name"], "code": bank["code"]}
                    for bank in data["data"]
                ]
                return {
                    "success": True,
                    "banks": banks,
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Failed to fetch banks"),
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch banks: {str(e)}",
            }

    def initialize_transaction(
        self,
        email: str,
        amount: Decimal,
        reference: Optional[str] = None,
        callback_url: Optional[str] = None,
        channels: Optional[list] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Initialize a Paystack transaction (for accepting payments)

        Args:
            email: Customer email
            amount: Amount in Naira (will be converted to kobo)
            reference: Optional transaction reference
            callback_url: URL to redirect after payment
            channels: Payment channels to allow e.g. ["card", "bank", "ussd"]
            metadata: Additional data to attach

        Returns: {
            "success": bool,
            "authorization_url": str,  # URL to redirect user for payment
            "access_code": str,
            "reference": str
        }
        """
        try:
            url = f"{self.base_url}/transaction/initialize"

            # Convert amount to kobo
            amount_in_kobo = int(amount * 100)

            payload = {
                "email": email,
                "amount": amount_in_kobo,
                "currency": "NGN",
            }

            if reference:
                payload["reference"] = reference
            if callback_url:
                payload["callback_url"] = callback_url
            if channels:
                payload["channels"] = channels
            if metadata:
                payload["metadata"] = metadata

            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            data = response.json()

            if response.status_code == 200 and data.get("status"):
                return {
                    "success": True,
                    "authorization_url": data["data"]["authorization_url"],
                    "access_code": data["data"]["access_code"],
                    "reference": data["data"]["reference"],
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Failed to initialize transaction"),
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Transaction initialization failed: {str(e)}",
            }

    def verify_transaction(self, reference: str) -> Dict:
        """
        Verify a Paystack transaction status

        Args:
            reference: Transaction reference to verify

        Returns: {
            "success": bool,
            "status": str,  # "success", "failed", "abandoned"
            "amount": Decimal,
            "customer_email": str,
            "paid_at": str
        }
        """
        try:
            url = f"{self.base_url}/transaction/verify/{reference}"

            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()

            if response.status_code == 200 and data.get("status"):
                txn_data = data["data"]
                return {
                    "success": True,
                    "status": txn_data["status"],
                    "amount": Decimal(txn_data["amount"]) / 100,  # Convert from kobo
                    "customer_email": txn_data["customer"]["email"],
                    "paid_at": txn_data.get("paid_at", ""),
                    "reference": txn_data["reference"],
                    "response": txn_data,
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Transaction verification failed"),
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Transaction verification failed: {str(e)}",
            }


# Create global instance
paystack_service = PaystackService()
