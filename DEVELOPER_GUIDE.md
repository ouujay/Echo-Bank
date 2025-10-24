# EchoBank - Complete Developer Guide

**This guide provides EXACT specifications, code examples, and step-by-step instructions for all 3 developers.**

---

## Table of Contents
1. [API Specifications](#api-specifications)
2. [Database Schema](#database-schema)
3. [Developer 1 Guide](#developer-1-backend-core--ai)
4. [Developer 2 Guide](#developer-2-transactions--auth)
5. [Developer 3 Guide](#developer-3-frontend)
6. [Testing Guide](#testing-guide)
7. [Deployment Guide](#deployment-guide)

---

## API Specifications

### Base URL
- **Development:** `http://localhost:8000`
- **Production:** `https://echobank-api.azurewebsites.net`

### Authentication
All endpoints (except health check) require JWT token in header:
```
Authorization: Bearer <jwt_token>
```

---

## 🔵 API Endpoints - Complete Specification

### 1. Voice Transcription

**Endpoint:** `POST /api/v1/voice/transcribe`

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Request Body:**
```
audio: File (audio/wav, audio/mp3, audio/webm)
session_id: string (optional)
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "transcript": "Send five thousand naira to John",
    "confidence": 0.95,
    "session_id": "sess_abc123",
    "timestamp": "2025-10-24T18:30:00Z"
  }
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "VOICE_UNCLEAR",
    "message": "Voice not clear. Please speak again.",
    "retry_count": 1
  }
}
```

---

### 2. Intent Recognition

**Endpoint:** `POST /api/v1/voice/intent`

**Request Body:**
```json
{
  "transcript": "Send five thousand naira to John",
  "session_id": "sess_abc123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "intent": "transfer",
    "confidence": 0.92,
    "entities": {
      "action": "send",
      "amount": 5000,
      "currency": "NGN",
      "recipient": "John"
    },
    "next_step": "verify_recipient"
  }
}
```

**Possible Intents:**
- `transfer` - Send money
- `check_balance` - Check account balance
- `add_recipient` - Add new beneficiary
- `cancel` - Cancel current operation
- `confirm` - Confirm transaction
- `unknown` - Intent not recognized

---

### 3. Search Recipients

**Endpoint:** `GET /api/v1/recipients/search?name=John`

**Query Parameters:**
```
name: string (required)
limit: integer (optional, default: 5)
```

**Response (200 OK) - Single Match:**
```json
{
  "success": true,
  "data": {
    "recipients": [
      {
        "id": "recp_123",
        "name": "John Okafor",
        "account_number": "0123456789",
        "bank_name": "Zenith Bank",
        "bank_code": "057"
      }
    ],
    "match_type": "single",
    "message": "Found John Okafor at Zenith Bank."
  }
}
```

**Response (200 OK) - Multiple Matches:**
```json
{
  "success": true,
  "data": {
    "recipients": [
      {
        "id": "recp_123",
        "name": "John Okafor",
        "account_number": "0123456789",
        "bank_name": "Zenith Bank"
      },
      {
        "id": "recp_456",
        "name": "John Adeyemi",
        "account_number": "9876543210",
        "bank_name": "GTBank"
      }
    ],
    "match_type": "multiple",
    "message": "I found 2 Johns. Say 1 for John Okafor or 2 for John Adeyemi."
  }
}
```

**Response (404 Not Found):**
```json
{
  "success": false,
  "error": {
    "code": "RECIPIENT_NOT_FOUND",
    "message": "I couldn't find John in your contacts.",
    "suggestion": "Say 'add new' to add them."
  }
}
```

---

### 4. Initiate Transfer

**Endpoint:** `POST /api/v1/transfers/initiate`

**Request Body:**
```json
{
  "recipient_id": "recp_123",
  "amount": 5000,
  "session_id": "sess_abc123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "transfer_id": "txn_abc123",
    "status": "pending_pin",
    "recipient": {
      "name": "John Okafor",
      "account_number": "0123456789",
      "bank_name": "Zenith Bank"
    },
    "amount": 5000,
    "currency": "NGN",
    "current_balance": 45320,
    "new_balance": 40320,
    "message": "Sending ₦5,000 to John Okafor. Please say your 4-digit PIN."
  }
}
```

**Response (400 Bad Request) - Insufficient Balance:**
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_BALANCE",
    "message": "Your balance is ₦3,000. You cannot send ₦5,000.",
    "current_balance": 3000,
    "requested_amount": 5000
  }
}
```

**Response (400 Bad Request) - Limit Exceeded:**
```json
{
  "success": false,
  "error": {
    "code": "LIMIT_EXCEEDED",
    "message": "Your daily limit is ₦50,000. You've used ₦48,000.",
    "daily_limit": 50000,
    "used_amount": 48000,
    "remaining": 2000,
    "suggestion": "Would you like to send ₦2,000 instead?"
  }
}
```

---

### 5. Verify PIN

**Endpoint:** `POST /api/v1/transfers/{transfer_id}/verify-pin`

**Request Body:**
```json
{
  "pin": "1234"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "transfer_id": "txn_abc123",
    "status": "pending_confirmation",
    "pin_verified": true,
    "message": "PIN verified. Say 'confirm' to complete the transfer."
  }
}
```

**Response (401 Unauthorized) - Wrong PIN:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_PIN",
    "message": "Incorrect PIN. You have 2 attempts remaining.",
    "attempts_remaining": 2
  }
}
```

**Response (403 Forbidden) - Locked:**
```json
{
  "success": false,
  "error": {
    "code": "PIN_LOCKED",
    "message": "Too many incorrect attempts. Locked for 30 minutes.",
    "locked_until": "2025-10-24T19:00:00Z"
  }
}
```

---

### 6. Confirm Transfer

**Endpoint:** `POST /api/v1/transfers/{transfer_id}/confirm`

**Request Body:**
```json
{
  "confirmation": "confirm"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "transfer_id": "txn_abc123",
    "status": "completed",
    "recipient": {
      "name": "John Okafor",
      "account_number": "0123456789"
    },
    "amount": 5000,
    "transaction_ref": "REF123456789",
    "timestamp": "2025-10-24T18:35:00Z",
    "new_balance": 40320,
    "message": "✅ Transfer successful! ₦5,000 sent to John Okafor. New balance: ₦40,320."
  }
}
```

**Response (500 Internal Server Error) - Transfer Failed:**
```json
{
  "success": false,
  "error": {
    "code": "TRANSFER_FAILED",
    "message": "Transfer failed due to a network error. Your money was not deducted.",
    "retry_available": true
  }
}
```

---

### 7. Cancel Transfer

**Endpoint:** `POST /api/v1/transfers/{transfer_id}/cancel`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "transfer_id": "txn_abc123",
    "status": "cancelled",
    "message": "Transfer cancelled. No money was sent."
  }
}
```

---

### 8. Get Session State

**Endpoint:** `GET /api/v1/voice/session/{session_id}`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "session_id": "sess_abc123",
    "user_id": "user_001",
    "current_step": "pending_pin",
    "context": {
      "transfer_id": "txn_abc123",
      "recipient": "John Okafor",
      "amount": 5000,
      "pin_attempts": 1
    },
    "created_at": "2025-10-24T18:30:00Z",
    "expires_at": "2025-10-24T19:00:00Z"
  }
}
```

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR(10) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    pin_hash VARCHAR(255) NOT NULL,
    balance DECIMAL(15, 2) DEFAULT 0.00,
    daily_limit DECIMAL(15, 2) DEFAULT 50000.00,
    is_active BOOLEAN DEFAULT TRUE,
    pin_locked_until TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Recipients Table
```sql
CREATE TABLE recipients (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    account_number VARCHAR(10) NOT NULL,
    bank_name VARCHAR(100) NOT NULL,
    bank_code VARCHAR(10) NOT NULL,
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_ref VARCHAR(50) UNIQUE NOT NULL,
    sender_id INTEGER REFERENCES users(id),
    recipient_id INTEGER REFERENCES recipients(id),
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'NGN',
    status VARCHAR(20) DEFAULT 'pending',
    -- status: pending, pending_pin, pending_confirmation, completed, failed, cancelled
    session_id VARCHAR(100),
    paystack_transfer_code VARCHAR(100),
    failure_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL
);
```

### Sessions Table
```sql
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    context JSONB,
    current_step VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Conversation Logs Table (for debugging)
```sql
CREATE TABLE conversation_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    user_id INTEGER REFERENCES users(id),
    speaker VARCHAR(10), -- 'user' or 'bot'
    message TEXT NOT NULL,
    intent VARCHAR(50),
    confidence DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Developer 1: Backend Core & AI

### File Structure You Need to Create

```
backend/app/
├── services/
│   ├── whisper.py      ← YOU CREATE THIS
│   ├── llm.py          ← YOU CREATE THIS
│   └── __init__.py
├── api/
│   ├── voice.py        ← YOU CREATE THIS
│   └── __init__.py
├── models/
│   ├── user.py         ← YOU CREATE THIS
│   ├── recipient.py    ← YOU CREATE THIS
│   ├── transaction.py  ← YOU CREATE THIS
│   ├── session.py      ← YOU CREATE THIS
│   └── __init__.py
```

---

### Step 1: Create Whisper Service

**File:** `backend/app/services/whisper.py`

```python
import openai
from app.core.config import settings
from fastapi import UploadFile
import tempfile
import os

class WhisperService:
    def __init__(self):
        openai.api_key = settings.WHISPERAPI

    async def transcribe_audio(self, audio_file: UploadFile) -> dict:
        """
        Transcribe audio file to text using OpenAI Whisper

        Args:
            audio_file: Audio file from user

        Returns:
            {
                "transcript": str,
                "confidence": float,
                "language": str
            }
        """
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                content = await audio_file.read()
                temp_audio.write(content)
                temp_audio_path = temp_audio.name

            # Transcribe using Whisper
            with open(temp_audio_path, "rb") as audio:
                transcript = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio,
                    language="en"  # Nigerian English
                )

            # Clean up temp file
            os.unlink(temp_audio_path)

            return {
                "transcript": transcript["text"],
                "confidence": 0.95,  # Whisper doesn't return confidence, use default
                "language": "en"
            }

        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")

whisper_service = WhisperService()
```

---

### Step 2: Create LLM Service

**File:** `backend/app/services/llm.py`

```python
import openai
from app.core.config import settings
import json

class LLMService:
    def __init__(self):
        # Use Together AI or OpenAI
        openai.api_key = settings.TOGETHER_API_KEY
        openai.api_base = "https://api.together.xyz/v1"  # If using Together AI

    async def parse_intent(self, transcript: str, context: dict = None) -> dict:
        """
        Parse user intent from transcript

        Args:
            transcript: Transcribed text from user
            context: Current conversation context

        Returns:
            {
                "intent": str,
                "confidence": float,
                "entities": dict,
                "next_step": str
            }
        """

        # Create prompt for LLM
        system_prompt = """
You are a banking assistant. Parse user intent for money transfers.
Extract: action, recipient name, amount.
Respond ONLY with JSON in this exact format:
{
  "intent": "transfer|check_balance|add_recipient|cancel|confirm|unknown",
  "confidence": 0.0-1.0,
  "entities": {
    "action": "send|pay|transfer",
    "recipient": "name",
    "amount": number,
    "currency": "NGN"
  },
  "next_step": "verify_recipient|verify_pin|confirm|complete"
}
"""

        user_prompt = f"User said: '{transcript}'"

        if context:
            user_prompt += f"\nContext: {json.dumps(context)}"

        try:
            response = openai.ChatCompletion.create(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",  # or "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": {},
                "next_step": "clarify",
                "error": str(e)
            }

llm_service = LLMService()
```

---

### Step 3: Create Voice API Endpoints

**File:** `backend/app/api/voice.py`

```python
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.whisper import whisper_service
from app.services.llm import llm_service
from app.utils.session import session_store
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])

class IntentRequest(BaseModel):
    transcript: str
    session_id: str = None

class TranscribeResponse(BaseModel):
    success: bool
    data: dict

@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    session_id: str = None
):
    """
    Transcribe audio to text using Whisper API
    """
    try:
        # Generate session ID if not provided
        if not session_id:
            session_id = f"sess_{uuid.uuid4().hex[:8]}"

        # Transcribe audio
        result = await whisper_service.transcribe_audio(audio)

        # Store in session
        session_store.set(session_id, {
            "last_transcript": result["transcript"],
            "timestamp": "2025-10-24T18:30:00Z"
        })

        return {
            "success": True,
            "data": {
                "transcript": result["transcript"],
                "confidence": result["confidence"],
                "session_id": session_id,
                "timestamp": "2025-10-24T18:30:00Z"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail={
            "code": "VOICE_UNCLEAR",
            "message": str(e)
        })

@router.post("/intent")
async def parse_intent(request: IntentRequest):
    """
    Parse intent from transcript using LLM
    """
    try:
        # Get session context
        context = None
        if request.session_id:
            context = session_store.get(request.session_id)

        # Parse intent
        result = await llm_service.parse_intent(request.transcript, context)

        # Update session
        if request.session_id:
            session_data = session_store.get(request.session_id) or {}
            session_data["last_intent"] = result
            session_store.set(request.session_id, session_data)

        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """
    Get current session state
    """
    session_data = session_store.get(session_id)

    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "success": True,
        "data": {
            "session_id": session_id,
            **session_data
        }
    }
```

---

### Step 4: Create Database Models

**File:** `backend/app/models/user.py`

```python
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(10), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(20))
    pin_hash = Column(String(255), nullable=False)
    balance = Column(Numeric(15, 2), default=0.00)
    daily_limit = Column(Numeric(15, 2), default=50000.00)
    is_active = Column(Boolean, default=True)
    pin_locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

**File:** `backend/app/models/transaction.py`

```python
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .user import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_ref = Column(String(50), unique=True, nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    recipient_id = Column(Integer, ForeignKey("recipients.id"))
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="NGN")
    status = Column(String(20), default="pending")
    session_id = Column(String(100))
    paystack_transfer_code = Column(String(100))
    failure_reason = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
```

---

### Step 5: Register Your Routes

**File:** `backend/app/main.py` (UPDATE THIS)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import voice  # ← ADD THIS

app = FastAPI(
    title="EchoBank API",
    description="Voice-powered banking assistant API",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers ← ADD THESE
app.include_router(voice.router)

@app.get("/")
async def root():
    return {
        "message": "EchoBank API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

### Testing Your Work

**Test Transcription:**
```bash
curl -X POST http://localhost:8000/api/v1/voice/transcribe \
  -F "audio=@test_audio.wav"
```

**Test Intent:**
```bash
curl -X POST http://localhost:8000/api/v1/voice/intent \
  -H "Content-Type: application/json" \
  -d '{"transcript": "Send 5000 naira to John"}'
```

---

## Developer 2: Transactions & Auth

### File Structure

```
backend/app/
├── services/
│   ├── auth.py         ← YOU CREATE THIS
│   ├── transfers.py    ← YOU CREATE THIS
│   ├── paystack.py     ← YOU CREATE THIS
│   └── __init__.py
├── api/
│   ├── recipients.py   ← YOU CREATE THIS
│   ├── transfers.py    ← YOU CREATE THIS
│   └── __init__.py
```

---

### Step 1: Create Auth Service

**File:** `backend/app/services/auth.py`

```python
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.models.user import User
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:

    @staticmethod
    def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
        """Verify PIN matches hash"""
        return pwd_context.verify(plain_pin, hashed_pin)

    @staticmethod
    def hash_pin(pin: str) -> str:
        """Hash PIN for storage"""
        return pwd_context.hash(pin)

    @staticmethod
    async def check_pin_attempts(user: User, db: Session) -> bool:
        """Check if user is locked out"""
        if user.pin_locked_until:
            if datetime.utcnow() < user.pin_locked_until:
                return False  # Still locked
            else:
                # Unlock user
                user.pin_locked_until = None
                db.commit()
        return True

    @staticmethod
    async def record_pin_failure(user: User, db: Session, attempt_count: int):
        """Lock user after 3 failed attempts"""
        if attempt_count >= 3:
            user.pin_locked_until = datetime.utcnow() + timedelta(minutes=30)
            db.commit()

auth_service = AuthService()
```

---

### Step 2: Create Transfer Service

**File:** `backend/app/services/transfers.py`

```python
from app.models.transaction import Transaction
from app.models.user import User
from app.models.recipient import Recipient
from sqlalchemy.orm import Session
from decimal import Decimal
import uuid

class TransferService:

    @staticmethod
    async def check_balance(user: User, amount: Decimal) -> dict:
        """Check if user has sufficient balance"""
        if user.balance < amount:
            return {
                "sufficient": False,
                "current_balance": float(user.balance),
                "requested_amount": float(amount)
            }
        return {"sufficient": True}

    @staticmethod
    async def check_daily_limit(user: User, amount: Decimal, db: Session) -> dict:
        """Check if transfer exceeds daily limit"""
        from datetime import datetime, timedelta
        from sqlalchemy import func

        # Get today's transactions
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
        today_transactions = db.query(func.sum(Transaction.amount)).filter(
            Transaction.sender_id == user.id,
            Transaction.status == "completed",
            Transaction.created_at >= today_start
        ).scalar() or Decimal(0)

        total_with_new = today_transactions + amount

        if total_with_new > user.daily_limit:
            return {
                "within_limit": False,
                "daily_limit": float(user.daily_limit),
                "used_amount": float(today_transactions),
                "remaining": float(user.daily_limit - today_transactions),
                "requested": float(amount)
            }
        return {"within_limit": True}

    @staticmethod
    async def create_transaction(
        sender: User,
        recipient: Recipient,
        amount: Decimal,
        session_id: str,
        db: Session
    ) -> Transaction:
        """Create a pending transaction"""
        transaction = Transaction(
            transaction_ref=f"REF{uuid.uuid4().hex[:10].upper()}",
            sender_id=sender.id,
            recipient_id=recipient.id,
            amount=amount,
            status="pending_pin",
            session_id=session_id
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    async def execute_transfer(transaction: Transaction, db: Session) -> dict:
        """Execute the actual transfer"""
        try:
            # Deduct from sender
            sender = transaction.sender
            sender.balance -= transaction.amount

            # Update transaction status
            transaction.status = "completed"
            transaction.completed_at = datetime.utcnow()

            db.commit()

            return {
                "success": True,
                "new_balance": float(sender.balance)
            }
        except Exception as e:
            db.rollback()
            transaction.status = "failed"
            transaction.failure_reason = str(e)
            db.commit()
            return {
                "success": False,
                "error": str(e)
            }

transfer_service = TransferService()
```

---

### Step 3: Create Recipients API

**File:** `backend/app/api/recipients.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.recipient import Recipient
from app.models.user import User
from typing import List

router = APIRouter(prefix="/api/v1/recipients", tags=["recipients"])

# Dependency to get DB session (you'll create this)
def get_db():
    # TODO: Implement database session
    pass

@router.get("/search")
async def search_recipients(
    name: str,
    limit: int = 5,
    user_id: int = 1,  # TODO: Get from JWT
    db: Session = Depends(get_db)
):
    """Search for recipients by name"""

    # Search in user's saved recipients
    recipients = db.query(Recipient).filter(
        Recipient.user_id == user_id,
        Recipient.name.ilike(f"%{name}%")
    ).limit(limit).all()

    if not recipients:
        raise HTTPException(status_code=404, detail={
            "code": "RECIPIENT_NOT_FOUND",
            "message": f"I couldn't find {name} in your contacts.",
            "suggestion": "Say 'add new' to add them."
        })

    if len(recipients) == 1:
        recp = recipients[0]
        return {
            "success": True,
            "data": {
                "recipients": [{
                    "id": recp.id,
                    "name": recp.name,
                    "account_number": recp.account_number,
                    "bank_name": recp.bank_name,
                    "bank_code": recp.bank_code
                }],
                "match_type": "single",
                "message": f"Found {recp.name} at {recp.bank_name}."
            }
        }
    else:
        return {
            "success": True,
            "data": {
                "recipients": [
                    {
                        "id": r.id,
                        "name": r.name,
                        "account_number": r.account_number,
                        "bank_name": r.bank_name
                    }
                    for r in recipients
                ],
                "match_type": "multiple",
                "message": f"I found {len(recipients)} matches. Say 1 for {recipients[0].name} or 2 for {recipients[1].name}."
            }
        }
```

---

### Step 4: Create Transfers API

**File:** `backend/app/api/transfers.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.services.transfers import transfer_service
from app.services.auth import auth_service
from app.models.transaction import Transaction
from app.models.user import User
from app.models.recipient import Recipient
from decimal import Decimal

router = APIRouter(prefix="/api/v1/transfers", tags=["transfers"])

class InitiateTransferRequest(BaseModel):
    recipient_id: int
    amount: float
    session_id: str

class VerifyPinRequest(BaseModel):
    pin: str

@router.post("/initiate")
async def initiate_transfer(
    request: InitiateTransferRequest,
    user_id: int = 1,  # TODO: Get from JWT
    db: Session = Depends(get_db)
):
    """Initiate a new transfer"""

    # Get user and recipient
    user = db.query(User).filter(User.id == user_id).first()
    recipient = db.query(Recipient).filter(Recipient.id == request.recipient_id).first()

    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    amount = Decimal(str(request.amount))

    # Check balance
    balance_check = await transfer_service.check_balance(user, amount)
    if not balance_check["sufficient"]:
        raise HTTPException(status_code=400, detail={
            "code": "INSUFFICIENT_BALANCE",
            "message": f"Your balance is ₦{balance_check['current_balance']:,.0f}. You cannot send ₦{balance_check['requested_amount']:,.0f}.",
            **balance_check
        })

    # Check daily limit
    limit_check = await transfer_service.check_daily_limit(user, amount, db)
    if not limit_check["within_limit"]:
        raise HTTPException(status_code=400, detail={
            "code": "LIMIT_EXCEEDED",
            **limit_check
        })

    # Create transaction
    transaction = await transfer_service.create_transaction(
        user, recipient, amount, request.session_id, db
    )

    return {
        "success": True,
        "data": {
            "transfer_id": transaction.transaction_ref,
            "status": "pending_pin",
            "recipient": {
                "name": recipient.name,
                "account_number": recipient.account_number,
                "bank_name": recipient.bank_name
            },
            "amount": float(amount),
            "currency": "NGN",
            "current_balance": float(user.balance),
            "new_balance": float(user.balance - amount),
            "message": f"Sending ₦{amount:,.0f} to {recipient.name}. Please say your 4-digit PIN."
        }
    }

@router.post("/{transfer_id}/verify-pin")
async def verify_pin(
    transfer_id: str,
    request: VerifyPinRequest,
    user_id: int = 1,  # TODO: Get from JWT
    db: Session = Depends(get_db)
):
    """Verify PIN for transfer"""

    # Get transaction and user
    transaction = db.query(Transaction).filter(
        Transaction.transaction_ref == transfer_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    user = db.query(User).filter(User.id == user_id).first()

    # Check if locked
    if not await auth_service.check_pin_attempts(user, db):
        locked_until = user.pin_locked_until
        raise HTTPException(status_code=403, detail={
            "code": "PIN_LOCKED",
            "message": "Too many incorrect attempts. Locked for 30 minutes.",
            "locked_until": locked_until.isoformat()
        })

    # Verify PIN
    if auth_service.verify_pin(request.pin, user.pin_hash):
        # PIN correct - update transaction
        transaction.status = "pending_confirmation"
        db.commit()

        return {
            "success": True,
            "data": {
                "transfer_id": transfer_id,
                "status": "pending_confirmation",
                "pin_verified": True,
                "message": "PIN verified. Say 'confirm' to complete the transfer."
            }
        }
    else:
        # PIN incorrect
        # TODO: Track attempts in session
        attempts = 1  # Get from session
        await auth_service.record_pin_failure(user, db, attempts)

        raise HTTPException(status_code=401, detail={
            "code": "INVALID_PIN",
            "message": f"Incorrect PIN. You have {3 - attempts} attempts remaining.",
            "attempts_remaining": 3 - attempts
        })

@router.post("/{transfer_id}/confirm")
async def confirm_transfer(
    transfer_id: str,
    db: Session = Depends(get_db)
):
    """Confirm and execute transfer"""

    transaction = db.query(Transaction).filter(
        Transaction.transaction_ref == transfer_id,
        Transaction.status == "pending_confirmation"
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found or not ready for confirmation")

    # Execute transfer
    result = await transfer_service.execute_transfer(transaction, db)

    if result["success"]:
        recipient = transaction.recipient
        return {
            "success": True,
            "data": {
                "transfer_id": transfer_id,
                "status": "completed",
                "recipient": {
                    "name": recipient.name,
                    "account_number": recipient.account_number
                },
                "amount": float(transaction.amount),
                "transaction_ref": transaction.transaction_ref,
                "timestamp": transaction.completed_at.isoformat(),
                "new_balance": result["new_balance"],
                "message": f"✅ Transfer successful! ₦{transaction.amount:,.0f} sent to {recipient.name}. New balance: ₦{result['new_balance']:,.0f}."
            }
        }
    else:
        raise HTTPException(status_code=500, detail={
            "code": "TRANSFER_FAILED",
            "message": "Transfer failed due to a network error. Your money was not deducted.",
            "error": result["error"]
        })

@router.post("/{transfer_id}/cancel")
async def cancel_transfer(
    transfer_id: str,
    db: Session = Depends(get_db)
):
    """Cancel pending transfer"""

    transaction = db.query(Transaction).filter(
        Transaction.transaction_ref == transfer_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.status == "completed":
        raise HTTPException(status_code=400, detail="Cannot cancel completed transaction")

    transaction.status = "cancelled"
    db.commit()

    return {
        "success": True,
        "data": {
            "transfer_id": transfer_id,
            "status": "cancelled",
            "message": "Transfer cancelled. No money was sent."
        }
    }
```

---

## Developer 3: Frontend

### File Structure

```
frontend/src/
├── components/
│   ├── VoiceModal/
│   │   ├── VoiceModal.jsx      ← YOU CREATE THIS
│   │   ├── VoiceModal.module.css
│   │   └── index.js
│   ├── Transcript/
│   │   ├── Transcript.jsx      ← YOU CREATE THIS
│   │   ├── Transcript.module.css
│   │   └── index.js
│   └── TransferFlow/
│       ├── PinModal.jsx         ← YOU CREATE THIS
│       ├── ConfirmModal.jsx     ← YOU CREATE THIS
│       └── index.js
├── services/
│   ├── api.js                   ← YOU CREATE THIS
│   ├── voiceService.js          ← YOU CREATE THIS
│   └── transferService.js       ← YOU CREATE THIS
├── hooks/
│   ├── useVoice.js              ← YOU CREATE THIS
│   └── useTransfer.js           ← YOU CREATE THIS
```

---

### Step 1: Create API Service

**File:** `frontend/src/services/api.js`

```javascript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      console.error('Unauthorized access');
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

### Step 2: Create Voice Service

**File:** `frontend/src/services/voiceService.js`

```javascript
import api from './api';

export const voiceService = {
  /**
   * Transcribe audio file to text
   */
  async transcribeAudio(audioBlob, sessionId = null) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    if (sessionId) {
      formData.append('session_id', sessionId);
    }

    const response = await api.post('/api/v1/voice/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  /**
   * Parse intent from transcript
   */
  async parseIntent(transcript, sessionId) {
    const response = await api.post('/api/v1/voice/intent', {
      transcript,
      session_id: sessionId,
    });

    return response.data;
  },

  /**
   * Get session state
   */
  async getSession(sessionId) {
    const response = await api.get(`/api/v1/voice/session/${sessionId}`);
    return response.data;
  },
};
```

---

### Step 3: Create Transfer Service

**File:** `frontend/src/services/transferService.js`

```javascript
import api from './api';

export const transferService = {
  /**
   * Search for recipients by name
   */
  async searchRecipients(name, limit = 5) {
    const response = await api.get('/api/v1/recipients/search', {
      params: { name, limit },
    });
    return response.data;
  },

  /**
   * Initiate a new transfer
   */
  async initiateTransfer(recipientId, amount, sessionId) {
    const response = await api.post('/api/v1/transfers/initiate', {
      recipient_id: recipientId,
      amount,
      session_id: sessionId,
    });
    return response.data;
  },

  /**
   * Verify PIN for transfer
   */
  async verifyPin(transferId, pin) {
    const response = await api.post(
      `/api/v1/transfers/${transferId}/verify-pin`,
      { pin }
    );
    return response.data;
  },

  /**
   * Confirm transfer
   */
  async confirmTransfer(transferId) {
    const response = await api.post(
      `/api/v1/transfers/${transferId}/confirm`,
      { confirmation: 'confirm' }
    );
    return response.data;
  },

  /**
   * Cancel transfer
   */
  async cancelTransfer(transferId) {
    const response = await api.post(`/api/v1/transfers/${transferId}/cancel`);
    return response.data;
  },
};
```

---

### Step 4: Create Voice Hook

**File:** `frontend/src/hooks/useVoice.js`

```javascript
import { useState, useRef } from 'react';
import { voiceService } from '../services/voiceService';

export const useVoice = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await processAudio(audioBlob);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setError(null);
    } catch (err) {
      setError('Microphone access denied');
      console.error('Error accessing microphone:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  const processAudio = async (audioBlob) => {
    setIsProcessing(true);
    try {
      const response = await voiceService.transcribeAudio(audioBlob);
      setTranscript(response.data.transcript);
      setIsProcessing(false);
      return response.data;
    } catch (err) {
      setError('Failed to process audio');
      setIsProcessing(false);
      throw err;
    }
  };

  return {
    isRecording,
    isProcessing,
    transcript,
    error,
    startRecording,
    stopRecording,
  };
};
```

---

### Step 5: Create Voice Modal Component

**File:** `frontend/src/components/VoiceModal/VoiceModal.jsx`

```javascript
import { useState } from 'react';
import { useVoice } from '../../hooks/useVoice';
import { voiceService } from '../../services/voiceService';
import styles from './VoiceModal.module.css';

export const VoiceModal = ({ onClose, onTranscript }) => {
  const { isRecording, isProcessing, transcript, startRecording, stopRecording } = useVoice();
  const [sessionId] = useState(`sess_${Math.random().toString(36).substr(2, 9)}`);

  const handleVoiceClick = async () => {
    if (!isRecording && !isProcessing) {
      await startRecording();

      // Auto-stop after 5 seconds
      setTimeout(() => {
        if (isRecording) {
          stopRecording();
        }
      }, 5000);
    }
  };

  const handleTranscriptComplete = async () => {
    if (transcript) {
      // Parse intent
      const intentResponse = await voiceService.parseIntent(transcript, sessionId);
      onTranscript(transcript, intentResponse.data);
    }
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h2>Voice Assistant</h2>
          <button className={styles.closeBtn} onClick={onClose}>×</button>
        </div>

        <div className={styles.content}>
          <button
            className={`${styles.voiceButton} ${isRecording ? styles.recording : ''} ${isProcessing ? styles.processing : ''}`}
            onClick={handleVoiceClick}
            disabled={isProcessing}
          >
            <div className={styles.voiceButtonInner}>
              {isProcessing ? (
                <div className={styles.spinner}></div>
              ) : (
                <>
                  <span className={styles.micIcon}>🎤</span>
                  {isRecording && (
                    <div className={styles.pulseRings}>
                      <div className={styles.pulseRing}></div>
                      <div className={styles.pulseRing}></div>
                      <div className={styles.pulseRing}></div>
                    </div>
                  )}
                </>
              )}
            </div>
          </button>

          <p className={styles.hint}>
            {isRecording ? 'Listening...' : isProcessing ? 'Processing...' : 'Tap to speak'}
          </p>

          {transcript && (
            <div className={styles.transcript}>
              <p className={styles.transcriptLabel}>You said:</p>
              <p className={styles.transcriptText}>{transcript}</p>
              <button className={styles.confirmBtn} onClick={handleTranscriptComplete}>
                Continue
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
```

**File:** `frontend/src/components/VoiceModal/VoiceModal.module.css`

```css
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: linear-gradient(135deg, #1a1f3a 0%, #0A0E27 100%);
  border-radius: 20px;
  padding: 30px;
  max-width: 500px;
  width: 90%;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header h2 {
  color: white;
  font-size: 24px;
  margin: 0;
}

.closeBtn {
  background: transparent;
  border: none;
  color: white;
  font-size: 32px;
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
}

.content {
  text-align: center;
}

.voiceButton {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #0066FF 0%, #0052CC 100%);
  cursor: pointer;
  position: relative;
  transition: all 0.3s;
  box-shadow: 0 10px 40px rgba(0, 102, 255, 0.3);
  margin: 0 auto 20px;
}

.voiceButton:hover:not(:disabled) {
  transform: scale(1.05);
}

.voiceButton.recording {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(0, 102, 255, 0.7);
  }
  70% {
    box-shadow: 0 0 0 30px rgba(0, 102, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(0, 102, 255, 0);
  }
}

.micIcon {
  font-size: 48px;
}

.hint {
  color: #A0AEC0;
  font-size: 16px;
  margin-bottom: 20px;
}

.transcript {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
}

.transcriptLabel {
  color: #A0AEC0;
  font-size: 14px;
  margin-bottom: 8px;
}

.transcriptText {
  color: white;
  font-size: 18px;
  margin-bottom: 16px;
}

.confirmBtn {
  background: linear-gradient(135deg, #00C853 0%, #00A843 100%);
  color: white;
  border: none;
  padding: 12px 32px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.confirmBtn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 200, 83, 0.3);
}
```

---

### Step 6: Update Main App

**File:** `frontend/src/App.jsx` (UPDATE THIS)

Add this import at the top:
```javascript
import { VoiceModal } from './components/VoiceModal/VoiceModal';
```

Add this state to your App component:
```javascript
const [showVoiceModal, setShowVoiceModal] = useState(false);
```

Add this handler:
```javascript
const handleTranscript = (transcript, intent) => {
  console.log('Transcript:', transcript);
  console.log('Intent:', intent);

  // Add to conversation
  setConversation(prev => [
    ...prev,
    { type: 'user', text: transcript },
    { type: 'bot', text: `Intent: ${intent.intent}` }
  ]);

  setShowVoiceModal(false);
};
```

Update the voice button:
```javascript
<button
  className={`voice-button`}
  onClick={() => setShowVoiceModal(true)}
>
  <div className="voice-button-inner">
    <div className="mic-icon">🎤</div>
  </div>
</button>
```

Add this before the closing `</div>` of the app:
```javascript
{showVoiceModal && (
  <VoiceModal
    onClose={() => setShowVoiceModal(false)}
    onTranscript={handleTranscript}
  />
)}
```

---

### Step 7: Create Environment File

**File:** `frontend/.env`

```
VITE_API_URL=http://localhost:8000
```

---

### Testing Your Work

**Test Voice Recording:**
1. Click the microphone button
2. Grant microphone access
3. Speak: "Send 5000 naira to John"
4. Check console for transcript and intent

**Test API Integration:**
```javascript
// In browser console
fetch('http://localhost:8000/api/v1/voice/intent', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    transcript: 'Send 5000 to John'
  })
}).then(r => r.json()).then(console.log);
```

---

## Testing Guide

### Backend Testing

**File:** `backend/tests/test_voice.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_parse_intent():
    response = client.post("/api/v1/voice/intent", json={
        "transcript": "Send 5000 naira to John"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["data"]["intent"] == "transfer"
    assert data["data"]["entities"]["amount"] == 5000
```

### Frontend Testing

**File:** `frontend/src/components/VoiceModal/VoiceModal.test.jsx`

```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import { VoiceModal } from './VoiceModal';

test('renders voice modal', () => {
  render(<VoiceModal onClose={() => {}} onTranscript={() => {}} />);
  expect(screen.getByText('Voice Assistant')).toBeInTheDocument();
});
```

---

## Quick Reference

### Common Commands

```bash
# Start backend
cd backend
uvicorn app.main:app --reload --port 8000

# Start frontend
cd frontend
npm run dev

# Run tests
pytest backend/tests/
npm test  # frontend

# Create database migration
alembic revision --autogenerate -m "Add users table"
alembic upgrade head

# Check API docs
open http://localhost:8000/docs
```

### API Response Codes

- `200` - Success
- `400` - Bad Request (validation error, insufficient balance, etc.)
- `401` - Unauthorized (wrong PIN)
- `403` - Forbidden (locked account)
- `404` - Not Found (recipient, transaction not found)
- `500` - Server Error (transfer failed)

---

## Need Help?

1. Check the API docs: http://localhost:8000/docs
2. Review the PRD: `informatioin for the project .txt`
3. Check GitHub issues
4. Ask in `#echobank-dev` Slack channel

---

**You now have EVERYTHING you need to build your assigned parts! 🚀**
