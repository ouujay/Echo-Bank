# Funbi User Setup - Complete! ✅

## New User Created: **Funbi Adeyemi**

### Account Details
- **Account Number**: `8523711419`
- **Account Balance**: ₦250,000.00
- **Bank**: Demo Bank (Company ID: 4)

---

## Recipients (3 Total)

| Name | Nickname | Account Number | Bank | Bank Code |
|------|----------|----------------|------|-----------|
| Tunde Bakare | Tunde | 2234567891 | First Bank | 011 |
| Chioma Okafor | Chi | 3345678912 | Zenith Bank | 057 |
| Bola Tinubu Jr | Bola | 4456789123 | UBA | 033 |

---

## How to Test Funbi's Account

### 1. **On EchoBank Demo Page** (http://localhost:5173)
Change the account number in `frontend/src/App.jsx`:
```javascript
const DEMO_ACCOUNT = '8523711419'  // Funbi's account
```

Then use voice commands:
- "Check my balance" → Should say "250,000 naira"
- "Show my recipients" → Should list Tunde, Chioma, and Bola
- "Send 5000 to Tunde" → Should initiate transfer
- "Transfer to Chi" → Should ask for amount

### 2. **On Demo Bank Widget** (http://localhost:3000)
Update the account number in Demo Bank's component to use Funbi's account.

---

## CORS Fixed ✅
Added `http://localhost:3000` to allowed origins in `backend/app/core/config.py`:
```python
CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:3000"
```

This allows the Demo Bank widget to call EchoBank API without CORS errors.

---

##  TTS Working ✅
- Uses **pyttsx3** (offline, no API calls)
- Generates **WAV audio** encoded as base64
- Fresh engine created per request (no blocking)
- Response time: ~2-3 seconds

---

## API Endpoints Tested

### Balance Check
```bash
curl http://127.0.0.1:8100/api/v1/accounts/8523711419/balance
```
Response:
```json
{
  "success": true,
  "account_number": "8523711419",
  "balance": 250000.0,
  "currency": "NGN"
}
```

### Recipients List
```bash
curl http://127.0.0.1:8100/api/v1/accounts/8523711419/beneficiaries
```
Response:
```json
{
  "success": true,
  "beneficiaries": [
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
```

---

## All Users in System

| User | Account Number | Balance | Recipients | Bank |
|------|----------------|---------|------------|------|
| John Doe | 6523711418 | ₦95,000 | 4 (John Doe, John Ade, John Epe, Mary) | Demo Bank |
| Funbi Adeyemi | 8523711419 | ₦250,000 | 3 (Tunde, Chioma, Bola) | Demo Bank |

---

## Voice Commands That Work

### Balance Queries
- "Check my balance"
- "What's my balance?"
- "How much money do I have?"

### Recipient Queries
- "Show my recipients"
- "List my beneficiaries"
- "Who can I send money to?"

### Transfer Commands
- "Send 5000 to Tunde"
- "Transfer money to Chi"
- "I want to send 10000 to Bola"

### Multiple John Recipients (Edge Case Handled!)
- "Send to John" → System asks which John (John Doe, John Ade, or John Epe)
- User can then clarify: "John Ade" or "John Doe"

---

## Running Services

All services running on localhost:

| Service | Port | URL | Status |
|---------|------|-----|--------|
| EchoBank API (Backend) | 8000 | http://127.0.0.1:8000 | ✅ Running |
| EchoBank Frontend | 5173 | http://localhost:5173 | ✅ Running |
| Demo Bank Frontend | 3000 | http://localhost:3000 | ✅ Running |
| Mock Bank API | 8100 | http://127.0.0.1:8100 | ✅ Running |

---

## What Was Fixed

### 1. **TTS Blocking Issue** ✅
- **Problem**: Second voice request would hang indefinitely
- **Cause**: pyttsx3 shared single engine instance across requests
- **Fix**: Create fresh engine for each TTS request, then clean up
- **Result**: Multiple requests work smoothly without delays

### 2. **CORS Issue** ✅
- **Problem**: Demo Bank widget (port 3000) blocked by CORS
- **Cause**: Port 3000 not in allowed origins
- **Fix**: Added `http://localhost:3000` to CORS_ORIGINS
- **Result**: Widget can now call EchoBank API successfully

### 3. **Recipient Retrieval** ✅
- **Problem**: Recipients sometimes failing to load
- **Cause**: Mock bank server was returning same recipients for all users
- **Fix**: Created per-account recipient mapping in mock server
- **Result**: Each user gets their own recipients

---

## Next Steps (Optional Improvements)

1. **Add more edge cases** (insufficient balance, invalid PIN, etc.)
2. **Improve TTS voice quality** (explore different pyttsx3 voices)
3. **Add transaction history** (list recent transfers)
4. **Implement airtime purchase** (buy airtime for phone numbers)
5. **Add bill payment** (DSTV, PHCN, etc.)

---

**Setup Complete!** 🎉
Both John Doe and Funbi can now use voice banking with TTS responses!
