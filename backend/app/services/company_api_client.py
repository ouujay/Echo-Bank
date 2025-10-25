"""
Company API Client

This service calls the COMPANY'S (bank's) API endpoints
Instead of using mock data, we call the real bank's API
"""
import httpx
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.company import Company, CompanyEndpoints


class CompanyAPIClient:
    """
    Client to call company's registered API endpoints
    """

    def __init__(self, company_id: int, db: Session):
        self.company_id = company_id
        self.db = db
        self.company = self._get_company()
        self.endpoints = self._get_endpoints()

        if not self.endpoints:
            raise ValueError(f"No endpoints configured for company {company_id}")

    def _get_company(self) -> Company:
        """Get company from database"""
        company = self.db.query(Company).filter(Company.id == self.company_id).first()
        if not company:
            raise ValueError(f"Company {self.company_id} not found")
        return company

    def _get_endpoints(self) -> Optional[CompanyEndpoints]:
        """Get company's configured endpoints"""
        return self.db.query(CompanyEndpoints).filter(
            CompanyEndpoints.company_id == self.company_id,
            CompanyEndpoints.is_active == True
        ).first()

    def _build_url(self, endpoint_path: str, **path_params) -> str:
        """Build full URL from base + endpoint"""
        url = self.endpoints.base_url.rstrip('/') + '/' + endpoint_path.lstrip('/')

        # Replace path parameters
        for key, value in path_params.items():
            url = url.replace(f"{{{key}}}", str(value))

        return url

    def _get_headers(self, user_token: str) -> Dict[str, str]:
        """Build request headers"""
        headers = {
            "Content-Type": "application/json"
        }

        # Add company's custom headers
        if self.endpoints.request_headers:
            headers.update(self.endpoints.request_headers)

        # Add auth header
        if self.endpoints.auth_type == "bearer":
            headers[self.endpoints.auth_header_name] = f"Bearer {user_token}"
        elif self.endpoints.auth_type == "api_key":
            headers[self.endpoints.auth_header_name] = user_token

        return headers

    async def get_balance(self, account_number: str, user_token: str) -> Dict[str, Any]:
        """
        Get account balance from company's API

        Args:
            account_number: User's account number
            user_token: User's auth token from the bank

        Returns:
            {"success": True, "balance": 95000.00}
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                url = self._build_url(
                    self.endpoints.get_balance_endpoint,
                    account_number=account_number
                )
                headers = self._get_headers(user_token)

                print(f"\n[API CLIENT] Attempt {attempt + 1}/{max_retries} - GET Balance")
                print(f"[API CLIENT] URL: {url}")
                print(f"[API CLIENT] Headers: {headers}")

                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(url, headers=headers)

                    print(f"[API CLIENT] Response Status: {response.status_code}")
                    print(f"[API CLIENT] Response Body: {response.text[:500]}")

                    response.raise_for_status()

                    data = response.json()

                    # Map their response to our format
                    # They might return {"data": {"balance": 95000}}
                    # We need {"balance": 95000}
                    balance = self._extract_balance(data)

                    print(f"[API CLIENT] Successfully got balance: {balance}")

                    return {
                        "success": True,
                        "balance": balance
                    }

            except httpx.TimeoutException as e:
                print(f"[API CLIENT ERROR] Timeout on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    return {"success": False, "error": f"Connection timeout to bank API after {max_retries} attempts"}
            except httpx.HTTPStatusError as e:
                print(f"[API CLIENT ERROR] HTTP {e.response.status_code}: {e.response.text}")
                return {"success": False, "error": f"Bank API error: {e.response.status_code}"}
            except Exception as e:
                print(f"[API CLIENT ERROR] Unexpected error on attempt {attempt + 1}: {type(e).__name__}: {str(e)}")
                if attempt == max_retries - 1:
                    return {"success": False, "error": f"Failed to connect to bank API: {str(e)}"}

    async def get_recipients(self, account_number: str, user_token: str) -> Dict[str, Any]:
        """
        Get saved recipients/beneficiaries from company's API

        Returns:
            {
                "success": True,
                "recipients": [
                    {"name": "John Doe", "account_number": "1234567890", "bank_code": "057"},
                    ...
                ]
            }
        """
        try:
            url = self._build_url(
                self.endpoints.get_recipients_endpoint,
                account_number=account_number
            )
            headers = self._get_headers(user_token)

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                data = response.json()
                recipients = self._extract_recipients(data)

                return {
                    "success": True,
                    "recipients": recipients
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def initiate_transfer(
        self,
        sender_account: str,
        recipient_account: str,
        bank_code: str,
        amount: float,
        narration: str,
        user_token: str
    ) -> Dict[str, Any]:
        """
        Initiate a transfer via company's API

        Returns:
            {
                "success": True,
                "transfer_id": "TXN123456",
                "fee": 10.50,
                "total": 1010.50
            }
        """
        try:
            url = self._build_url(self.endpoints.initiate_transfer_endpoint)
            headers = self._get_headers(user_token)

            payload = {
                "sender_account": sender_account,
                "recipient_account": recipient_account,
                "bank_code": bank_code,
                "amount": amount,
                "narration": narration
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                data = response.json()

                return {
                    "success": True,
                    "transfer_id": data.get("transfer_id") or data.get("transaction_id"),
                    "fee": data.get("fee", 0),
                    "total": data.get("total", amount)
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def confirm_transfer(
        self,
        transfer_id: str,
        pin: str,
        user_token: str
    ) -> Dict[str, Any]:
        """
        Confirm transfer with PIN via company's API

        Returns:
            {
                "success": True,
                "transaction_ref": "TXN123456",
                "new_balance": 93989.50
            }
        """
        try:
            url = self._build_url(
                self.endpoints.confirm_transfer_endpoint,
                transfer_id=transfer_id
            )
            headers = self._get_headers(user_token)

            payload = {"pin": pin}

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                data = response.json()

                return {
                    "success": True,
                    "transaction_ref": data.get("transaction_ref") or data.get("reference"),
                    "new_balance": data.get("new_balance") or data.get("balance")
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def cancel_transfer(
        self,
        transfer_id: str,
        user_token: str
    ) -> Dict[str, Any]:
        """Cancel a pending transfer"""
        if not self.endpoints.cancel_transfer_endpoint:
            return {"success": True, "message": "Transfer cancelled"}

        try:
            url = self._build_url(
                self.endpoints.cancel_transfer_endpoint,
                transfer_id=transfer_id
            )
            headers = self._get_headers(user_token)

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers)
                response.raise_for_status()

                return {"success": True, "message": "Transfer cancelled"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # Helper methods to extract data from company's response format
    def _extract_balance(self, response_data: Dict) -> float:
        """Extract balance from company's response format"""
        # Try common response formats
        if "balance" in response_data:
            return float(response_data["balance"])
        elif "data" in response_data and "balance" in response_data["data"]:
            return float(response_data["data"]["balance"])
        elif "account" in response_data and "balance" in response_data["account"]:
            return float(response_data["account"]["balance"])

        # Use custom mapping if provided
        if self.endpoints.response_mapping and "balance_path" in self.endpoints.response_mapping:
            path = self.endpoints.response_mapping["balance_path"].split(".")
            value = response_data
            for key in path:
                value = value[key]
            return float(value)

        raise ValueError("Could not extract balance from response")

    def _extract_recipients(self, response_data: Dict) -> list:
        """Extract recipients list from company's response format"""
        # If response is directly a list (Demo Bank format)
        if isinstance(response_data, list):
            return response_data

        # Try common response formats
        if "recipients" in response_data:
            return response_data["recipients"]
        elif "beneficiaries" in response_data:
            return response_data["beneficiaries"]
        elif "data" in response_data:
            if isinstance(response_data["data"], list):
                return response_data["data"]
            elif "recipients" in response_data["data"]:
                return response_data["data"]["recipients"]

        # Use custom mapping if provided
        if self.endpoints.response_mapping and "recipients_path" in self.endpoints.response_mapping:
            path = self.endpoints.response_mapping["recipients_path"].split(".")
            value = response_data
            for key in path:
                value = value[key]
            return value

        raise ValueError("Could not extract recipients from response")


# Factory function to get client for a company
def get_company_api_client(company_id: int, db: Session) -> CompanyAPIClient:
    """Get API client for a company"""
    return CompanyAPIClient(company_id=company_id, db=db)
