"""
Simple Mock Bank API Server for Testing
Simulates a bank's API endpoints that EchoBank will call
"""

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="Mock Bank API")

# Sample data - Recipients per account
RECIPIENTS_BY_ACCOUNT = {
    "6523711418": [  # John Doe's account
        {
            "name": "John Doe",
            "account_number": "1234567890",
            "bank_code": "033",
            "bank_name": "Access Bank"
        },
        {
            "name": "John Ade",
            "account_number": "0987654321",
            "bank_code": "058",
            "bank_name": "GTBank"
        },
        {
            "name": "John Epe",
            "account_number": "5555666677",
            "bank_code": "033",
            "bank_name": "Access Bank"
        },
        {
            "name": "Mary Johnson",
            "account_number": "1111222233",
            "bank_code": "044",
            "bank_name": "Access Bank"
        }
    ],
    "8523711419": [  # Funbi's account
        {
            "name": "Tunde Bakare",
            "account_number": "2234567891",
            "bank_code": "011",
            "bank_name": "First Bank"
        },
        {
            "name": "Chioma Okafor",
            "account_number": "3345678912",
            "bank_code": "057",
            "bank_name": "Zenith Bank"
        },
        {
            "name": "Bola Tinubu Jr",
            "account_number": "4456789123",
            "bank_code": "033",
            "bank_name": "UBA"
        }
    ]
}

# Balances per account
BALANCES = {
    "6523711418": 95000.00,  # John Doe
    "8523711419": 250000.00,  # Funbi
}

# In-memory storage for initiated transfers
initiated_transfers = {}
transfer_counter = 1


@app.get("/api/v1/accounts/{account_number}/balance")
async def get_balance(account_number: str, authorization: str = Header(None)):
    """Get account balance"""
    balance = BALANCES.get(account_number, 50000.00)  # Default balance
    return {
        "success": True,
        "account_number": account_number,
        "balance": balance,
        "currency": "NGN"
    }


@app.get("/api/v1/accounts/{account_number}/beneficiaries")
async def get_recipients(account_number: str, authorization: str = Header(None)):
    """Get list of beneficiaries/recipients"""
    recipients = RECIPIENTS_BY_ACCOUNT.get(account_number, [])
    return {
        "success": True,
        "beneficiaries": recipients
    }


class TransferInitiateRequest(BaseModel):
    sender_account: str
    recipient_account: str
    bank_code: str
    amount: float
    narration: Optional[str] = ""


@app.post("/api/v1/transfers/initiate")
async def initiate_transfer(request: TransferInitiateRequest, authorization: str = Header(None)):
    """Initiate a transfer"""
    global transfer_counter

    # Calculate fee (mock fee calculation)
    fee = 10.50 if request.amount < 5000 else 26.50
    total = request.amount + fee

    # Check if sufficient balance
    balance = BALANCES.get(request.sender_account, 50000.00)
    if total > balance:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Create transfer
    transfer_id = f"TXN{str(transfer_counter).zfill(6)}"
    transfer_counter += 1

    initiated_transfers[transfer_id] = {
        "transfer_id": transfer_id,
        "amount": request.amount,
        "fee": fee,
        "total": total,
        "recipient_account": request.recipient_account,
        "status": "pending"
    }

    return {
        "success": True,
        "transfer_id": transfer_id,
        "amount": request.amount,
        "fee": fee,
        "total": total,
        "status": "pending_confirmation"
    }


class TransferConfirmRequest(BaseModel):
    pin: str


@app.post("/api/v1/transfers/{transfer_id}/confirm")
async def confirm_transfer(transfer_id: str, request: TransferConfirmRequest, authorization: str = Header(None)):
    """Confirm transfer with PIN"""

    if transfer_id not in initiated_transfers:
        raise HTTPException(status_code=404, detail="Transfer not found")

    transfer = initiated_transfers[transfer_id]

    # Mock PIN verification (accept any 4-digit PIN)
    if len(request.pin) != 4 or not request.pin.isdigit():
        raise HTTPException(status_code=401, detail="Invalid PIN")

    # Mark as completed
    transfer["status"] = "completed"

    # Get balance from stored transfer data (we should store sender_account in initiate)
    balance = BALANCES.get(list(BALANCES.keys())[0], 50000.00)  # Simplified
    new_balance = balance - transfer["total"]

    return {
        "success": True,
        "transfer_id": transfer_id,
        "status": "completed",
        "transaction_ref": f"REF{transfer_id}",
        "new_balance": new_balance
    }


@app.post("/api/v1/transfers/{transfer_id}/cancel")
async def cancel_transfer(transfer_id: str, authorization: str = Header(None)):
    """Cancel a pending transfer"""

    if transfer_id in initiated_transfers:
        del initiated_transfers[transfer_id]

    return {
        "success": True,
        "message": "Transfer cancelled"
    }


class PinVerifyRequest(BaseModel):
    pin: str
    account_number: str


@app.post("/api/v1/auth/verify-pin")
async def verify_pin(request: PinVerifyRequest, authorization: str = Header(None)):
    """Verify user PIN"""

    # Mock: Accept any 4-digit PIN
    if len(request.pin) == 4 and request.pin.isdigit():
        return {
            "success": True,
            "verified": True
        }
    else:
        return {
            "success": False,
            "verified": False,
            "error": "Invalid PIN"
        }


@app.get("/")
async def root():
    return {
        "message": "Mock Bank API",
        "endpoints": {
            "balance": "/api/v1/accounts/{account_number}/balance",
            "recipients": "/api/v1/accounts/{account_number}/beneficiaries",
            "initiate_transfer": "/api/v1/transfers/initiate",
            "confirm_transfer": "/api/v1/transfers/{transfer_id}/confirm",
            "cancel_transfer": "/api/v1/transfers/{transfer_id}/cancel",
            "verify_pin": "/api/v1/auth/verify-pin"
        }
    }


if __name__ == "__main__":
    print("=" * 50)
    print("Mock Bank API Server Starting...")
    print("This simulates a bank's API for testing EchoBank")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8100)
