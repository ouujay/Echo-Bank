# Demo Bank App - Task Delegation Plan

## 🎯 Project Goal

Build a **Demo Bank Application** that integrates with EchoBank to demonstrate:
1. Real bank app with Paystack transfers
2. Voice banking powered by EchoBank
3. Complete integration story for judges

---

## 📊 System Architecture

```
                    ┌─────────────────────────────┐
                    │   Demo Bank Frontend        │
                    │   (React/React Native)      │
                    │                             │
                    │   - Login                   │
                    │   - Dashboard               │
                    │   - 🎤 Voice Button         │
                    │   - Transfers               │
                    │   - Recipients              │
                    └──────────┬──────────────────┘
                               │ HTTP/REST
                               ↓
                    ┌─────────────────────────────┐
                    │   Demo Bank Backend         │
                    │   (FastAPI + PostgreSQL)    │
                    │                             │
                    │   Database: demo_bank       │
                    │   - bank_users              │
                    │   - bank_accounts           │
                    │   - bank_recipients         │
                    │   - bank_transactions       │
                    │   - paystack_transfers      │
                    └──────┬──────────┬───────────┘
                           │          │
              ┌────────────┘          └────────────┐
              ↓                                    ↓
   ┌──────────────────────┐          ┌──────────────────────┐
   │   Paystack API       │          │   EchoBank Voice API │
   │                      │          │   (Existing)         │
   │   - Transfer funds   │          │                      │
   │   - Verify accounts  │          │   - Transcribe       │
   │   - Create recipient │          │   - Recognize intent │
   │   - Webhooks         │          │   - Orchestrate      │
   └──────────────────────┘          └──────────────────────┘
```

---

## 👥 Team Roles

### Developer A - Backend Core
**Skills:** Python, FastAPI, PostgreSQL, SQLAlchemy
**Time:** 6-8 hours

### Developer B - Paystack Integration
**Skills:** Python, API integration, Webhooks
**Time:** 4-6 hours

### Developer C - EchoBank Integration
**Skills:** Python, understanding EchoBank API
**Time:** 3-4 hours

### Developer D - Frontend
**Skills:** React/React Native, Voice APIs, TTS
**Time:** 8-10 hours

---

## 📋 Task Breakdown

### 🔵 TASK 1: Demo Bank Backend Core
**Assigned to:** Developer A
**Estimated time:** 6-8 hours
**Priority:** HIGH (blocking all other tasks)

#### Subtasks:

**1.1 Database Setup (1 hour)**
- [ ] Create PostgreSQL database `demo_bank`
- [ ] Run schema from `DEMO_BANK_SCHEMA.md`
- [ ] Create tables:
  - `bank_users`
  - `bank_accounts`
  - `bank_recipients`
  - `bank_transactions`
  - `paystack_transfers`
  - `daily_transfer_limits`
  - `auth_tokens`
- [ ] Add indexes for performance
- [ ] Insert test data (2 users, 2 accounts)

**Files to create:**
```
demo-bank/backend/
├── init_demo_bank.sql
└── seed_data.sql
```

**1.2 Database Models (1.5 hours)**
- [ ] Create SQLAlchemy models for all tables
- [ ] Add relationships (ForeignKey, back_populates)
- [ ] Add validation (check constraints, defaults)
- [ ] Create `database.py` for connection management

**Files to create:**
```
demo-bank/backend/app/models/
├── __init__.py
├── user.py          # BankUser model
├── account.py       # BankAccount model
├── recipient.py     # BankRecipient model
├── transaction.py   # BankTransaction model
└── paystack.py      # PaystackTransfer model
```

**1.3 Authentication API (2 hours)**
- [ ] `POST /api/auth/register` - Create user + account
- [ ] `POST /api/auth/login` - Email/password login, return JWT
- [ ] `POST /api/auth/verify-pin` - Verify 4-digit PIN
- [ ] `POST /api/auth/logout` - Revoke token
- [ ] JWT middleware for protected routes

**Files to create:**
```
demo-bank/backend/app/
├── api/auth.py
├── services/auth.py      # JWT creation/verification
└── core/security.py      # Password/PIN hashing
```

**1.4 Account Endpoints (1 hour)**
- [ ] `GET /api/accounts` - List user's accounts
- [ ] `GET /api/accounts/{id}/balance` - Get balance
- [ ] `GET /api/accounts/{id}/transactions` - Transaction history (paginated)

**Files to create:**
```
demo-bank/backend/app/api/accounts.py
```

**1.5 Recipient Endpoints (1.5 hours)**
- [ ] `GET /api/recipients` - List saved recipients
- [ ] `POST /api/recipients` - Add recipient (no Paystack yet)
- [ ] `GET /api/recipients/{id}` - Get single recipient
- [ ] `PUT /api/recipients/{id}/favorite` - Toggle favorite
- [ ] `DELETE /api/recipients/{id}` - Remove recipient

**Files to create:**
```
demo-bank/backend/app/api/recipients.py
```

**1.6 Transfer Endpoints (Basic) (2 hours)**
- [ ] `POST /api/transfers/initiate` - Create pending transfer
  - Check balance
  - Check daily limit
  - Create transaction with status='pending_pin'
- [ ] `POST /api/transfers/{id}/verify-pin` - Verify PIN
  - Set status='pending_confirmation'
- [ ] `POST /api/transfers/{id}/confirm` - Execute transfer
  - Deduct balance (NO Paystack yet - Developer B adds this)
  - Set status='completed'
- [ ] `GET /api/transfers/{id}` - Get transfer status
- [ ] `POST /api/transfers/{id}/cancel` - Cancel pending

**Files to create:**
```
demo-bank/backend/app/
├── api/transfers.py
└── services/transfer.py  # Transfer business logic
```

**Testing:**
- [ ] Create `test_demo_bank.http` with all endpoints
- [ ] Test full flow: Register → Login → Add recipient → Transfer

**Deliverable checklist:**
- [ ] Database schema created
- [ ] All models working
- [ ] Authentication works (login returns JWT)
- [ ] Can create account, add recipient
- [ ] Can initiate → verify PIN → confirm transfer
- [ ] Balance updates after transfer
- [ ] Transaction history shows transfers

---

### 🟢 TASK 2: Paystack Integration
**Assigned to:** Developer B
**Estimated time:** 4-6 hours
**Priority:** MEDIUM (depends on Task 1)
**Prerequisites:** Task 1 completed

#### Subtasks:

**2.1 Paystack Service Setup (1 hour)**
- [ ] Install `paystackapi` Python package
- [ ] Create Paystack service class
- [ ] Add Paystack test API keys to `.env`
- [ ] Test Paystack connection

**Files to create:**
```
demo-bank/backend/app/services/paystack.py
```

**Environment variables:**
```env
PAYSTACK_SECRET_KEY=sk_test_xxxxx
PAYSTACK_PUBLIC_KEY=pk_test_xxxxx
PAYSTACK_BASE_URL=https://api.paystack.co
```

**2.2 Paystack Recipient Creation (1.5 hours)**
- [ ] Implement name enquiry (account verification)
  - `POST https://api.paystack.co/bank/resolve`
  - Get account name from account number + bank code
- [ ] Implement recipient creation
  - `POST https://api.paystack.co/transferrecipient`
  - Store `recipient_code` in `bank_recipients.paystack_recipient_code`
- [ ] Update `POST /api/recipients` to create Paystack recipient
- [ ] Add `POST /api/recipients/verify` endpoint for name enquiry

**Paystack APIs to integrate:**
```python
# Name enquiry
def verify_account(account_number: str, bank_code: str) -> Dict:
    response = requests.get(
        f"{PAYSTACK_BASE_URL}/bank/resolve",
        params={"account_number": account_number, "bank_code": bank_code},
        headers={"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    )
    # Returns: {"account_name": "John Doe", "account_number": "0123456789"}

# Create recipient
def create_transfer_recipient(name: str, account_number: str, bank_code: str) -> str:
    response = requests.post(
        f"{PAYSTACK_BASE_URL}/transferrecipient",
        json={
            "type": "nuban",
            "name": name,
            "account_number": account_number,
            "bank_code": bank_code,
            "currency": "NGN"
        },
        headers={"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    )
    # Returns: {"recipient_code": "RCP_xxxxx"}
```

**2.3 Paystack Transfer Execution (2 hours)**
- [ ] Implement transfer initiation
  - `POST https://api.paystack.co/transfer`
  - Amount in kobo (₦5,000 = 500000 kobo)
  - Store `transfer_code` in `bank_transactions.paystack_transfer_code`
- [ ] Update `POST /api/transfers/{id}/confirm` to use Paystack
- [ ] Handle Paystack errors (insufficient balance, invalid account)
- [ ] Store Paystack response in `paystack_transfers` table

**Paystack Transfer API:**
```python
def initiate_paystack_transfer(recipient_code: str, amount: Decimal, reason: str) -> Dict:
    response = requests.post(
        f"{PAYSTACK_BASE_URL}/transfer",
        json={
            "source": "balance",
            "amount": int(amount * 100),  # Convert to kobo
            "recipient": recipient_code,
            "reason": reason,
            "currency": "NGN"
        },
        headers={"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    )
    # Returns: {"transfer_code": "TRF_xxxxx", "status": "pending"}
```

**2.4 Webhooks for Transfer Status (1.5 hours)**
- [ ] Create webhook endpoint: `POST /api/webhooks/paystack`
- [ ] Verify Paystack signature
- [ ] Handle `transfer.success` event → Update transaction status
- [ ] Handle `transfer.failed` event → Reverse transaction, restore balance
- [ ] Handle `transfer.reversed` event → Update status

**Files to create:**
```
demo-bank/backend/app/api/webhooks.py
```

**Webhook handler:**
```python
@router.post("/webhooks/paystack")
async def paystack_webhook(request: Request):
    # Verify signature
    signature = request.headers.get("x-paystack-signature")
    payload = await request.body()

    # Validate signature
    computed_signature = hmac.new(
        PAYSTACK_SECRET_KEY.encode(),
        payload,
        hashlib.sha512
    ).hexdigest()

    if signature != computed_signature:
        raise HTTPException(status_code=401)

    event = json.loads(payload)

    if event["event"] == "transfer.success":
        # Update transaction status to 'completed'
        pass
    elif event["event"] == "transfer.failed":
        # Reverse transaction, restore balance
        pass
```

**Testing:**
- [ ] Test name enquiry with test accounts
- [ ] Test creating Paystack recipient
- [ ] Test transfer initiation (use Paystack test mode)
- [ ] Test webhook handling (use Paystack webhook tester)

**Deliverable checklist:**
- [ ] Can verify account names via Paystack
- [ ] Paystack recipient created when adding beneficiary
- [ ] Transfer executes via Paystack API
- [ ] Webhook updates transfer status
- [ ] Failed transfers restore balance

---

### 🟡 TASK 3: EchoBank Integration
**Assigned to:** Developer C
**Estimated time:** 3-4 hours
**Priority:** MEDIUM (depends on Task 1)
**Prerequisites:** Task 1 completed, EchoBank API understanding

#### Subtasks:

**3.1 Study EchoBank Integration (30 mins)**
- [ ] Read `BANK_INTEGRATION_GUIDE.md`
- [ ] Review `BankAPIClient` interface
- [ ] Understand `MockBankAPI` implementation
- [ ] Test EchoBank voice orchestrator endpoints

**3.2 Implement DemoBankAPIClient (2 hours)**
- [ ] Create `DemoBankAPIClient` class implementing `BankAPIClient`
- [ ] Connect each method to Demo Bank API endpoints:
  - `verify_account()` → `POST /api/auth/verify-pin`
  - `get_balance()` → `GET /api/accounts/{id}/balance`
  - `get_recipients()` → `GET /api/recipients`
  - `initiate_transfer()` → `POST /api/transfers/initiate`
  - `confirm_transfer()` → `POST /api/transfers/{id}/confirm`
  - `cancel_transfer()` → `POST /api/transfers/{id}/cancel`
  - `add_recipient()` → `POST /api/recipients`
  - `verify_recipient_account()` → `POST /api/recipients/verify`

**Files to create:**
```
demo-bank/backend/app/integrations/
├── __init__.py
└── echobank_adapter.py
```

**Example implementation:**
```python
from app.integrations.bank_client import BankAPIClient
import requests

class DemoBankAPIClient(BankAPIClient):
    def __init__(self, demo_bank_api_url: str):
        self.api_url = demo_bank_api_url

    async def verify_account(self, account_number: str, pin: str) -> Dict:
        # Call Demo Bank's verify PIN endpoint
        response = requests.post(
            f"{self.api_url}/api/auth/verify-pin",
            json={"account_number": account_number, "pin": pin}
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "verified": True,
                "user_id": data["user_id"],
                "account_name": data["full_name"],
                "error": None
            }
        else:
            return {
                "verified": False,
                "error": "Invalid credentials"
            }

    async def get_balance(self, account_number: str, token: str) -> Dict:
        # Call Demo Bank's balance endpoint
        response = requests.get(
            f"{self.api_url}/api/accounts/balance",
            headers={"Authorization": f"Bearer {token}"},
            params={"account_number": account_number}
        )

        data = response.json()
        return {
            "success": True,
            "balance": Decimal(data["balance"]),
            "currency": "NGN",
            "available_balance": Decimal(data["balance"]),
            "error": None
        }

    # ... implement all other methods
```

**3.3 Update EchoBank Config (30 mins)**
- [ ] Update EchoBank to use `DemoBankAPIClient` instead of `MockBankAPI`
- [ ] Configure Demo Bank API URL in EchoBank's `.env`
- [ ] Test connection between EchoBank and Demo Bank

**Files to modify:**
```
echobank/backend/app/api/voice_orchestrator.py
```

**Change:**
```python
# Old
from app.integrations.mock_bank import mock_bank_client
bank_client = mock_bank_client

# New
from demo_bank.app.integrations.echobank_adapter import DemoBankAPIClient
bank_client = DemoBankAPIClient(
    demo_bank_api_url=os.getenv("DEMO_BANK_API_URL")
)
```

**3.4 Test Complete Voice Flow (1 hour)**
- [ ] Start Demo Bank backend
- [ ] Start EchoBank backend
- [ ] Test voice command: "What's my balance?"
- [ ] Test voice transfer: "Send 5000 to Sarah"
  - Should call Demo Bank initiate endpoint
  - Should ask for confirmation
  - Should ask for PIN
  - Should call Demo Bank confirm endpoint
  - Should execute via Paystack
- [ ] Verify transaction appears in Demo Bank database

**Testing:**
- [ ] Create `test_integration.http` for end-to-end tests
- [ ] Test each EchoBank voice flow

**Deliverable checklist:**
- [ ] `DemoBankAPIClient` implements all `BankAPIClient` methods
- [ ] EchoBank successfully calls Demo Bank API
- [ ] Voice command "check balance" works
- [ ] Voice transfer flow works end-to-end
- [ ] Paystack transfer executes from voice command

---

### 🟣 TASK 4: Demo Bank Frontend
**Assigned to:** Developer D
**Estimated time:** 8-10 hours
**Priority:** MEDIUM (can start in parallel with backend)

#### Subtasks:

**4.1 Project Setup (30 mins)**
- [ ] Create React/React Native project
- [ ] Install dependencies:
  - `axios` - API calls
  - `react-native-audio-recorder-player` - Voice recording
  - `react-native-tts` or Web Speech API - Text-to-speech
  - `@react-navigation` - Screen navigation
  - `react-redux` or Context API - State management
- [ ] Configure API base URL

**Files to create:**
```
demo-bank/frontend/
├── package.json
├── .env
└── src/
    ├── App.jsx
    ├── navigation/
    ├── screens/
    ├── components/
    └── services/
```

**4.2 API Service Layer (1 hour)**
- [ ] Create axios client with JWT interceptor
- [ ] Create auth service (login, register, logout)
- [ ] Create accounts service
- [ ] Create recipients service
- [ ] Create transfers service
- [ ] Create EchoBank voice service

**Files to create:**
```
demo-bank/frontend/src/services/
├── api.js              # Axios client
├── auth.js             # Authentication
├── accounts.js         # Account operations
├── recipients.js       # Recipients
├── transfers.js        # Transfers
└── echobank.js         # EchoBank Voice API
```

**Example:**
```javascript
// services/echobank.js
import axios from 'axios';

const ECHOBANK_API = process.env.REACT_APP_ECHOBANK_API_URL;

export const processVoiceAudio = async (audioBlob, accountNumber, token, sessionId) => {
  const formData = new FormData();
  formData.append('audio', audioBlob);

  const response = await axios.post(
    `${ECHOBANK_API}/api/v1/voice/process-audio`,
    formData,
    {
      headers: {
        'account_number': accountNumber,
        'token': token,
        'session_id': sessionId,
        'Content-Type': 'multipart/form-data'
      }
    }
  );

  return response.data;
};

export const processVoiceText = async (text, accountNumber, token, sessionId) => {
  const response = await axios.post(
    `${ECHOBANK_API}/api/v1/voice/process-text`,
    { text, account_number: accountNumber, token, session_id: sessionId }
  );

  return response.data;
};
```

**4.3 Login Screen (1.5 hours)**
- [ ] Email + Password inputs
- [ ] Login button
- [ ] Register link
- [ ] Error handling
- [ ] Store JWT token on success
- [ ] Navigate to Dashboard

**Files to create:**
```
demo-bank/frontend/src/screens/LoginScreen.jsx
```

**4.4 Dashboard Screen (2 hours)**
- [ ] Show account balance (large, prominent)
- [ ] Show account number
- [ ] Recent transactions list (5 most recent)
- [ ] Quick actions:
  - Transfer button
  - Recipients button
  - **🎤 Voice Assistant button** (prominent)
- [ ] Pull-to-refresh

**Files to create:**
```
demo-bank/frontend/src/screens/DashboardScreen.jsx
demo-bank/frontend/src/components/BalanceCard.jsx
demo-bank/frontend/src/components/TransactionList.jsx
```

**4.5 Voice Button Component (2.5 hours)** ⭐ CRITICAL
- [ ] Large microphone button (hold to speak)
- [ ] Voice recording (WAV format)
- [ ] Send audio to EchoBank API
- [ ] Display transcribed text
- [ ] **Speak response back to user (TTS)**
- [ ] Handle different actions:
  - `confirm_transfer` → Show confirmation modal
  - `request_pin` → Show PIN input
  - `complete` → Show success message
- [ ] Session management (keep session_id across conversation)

**Files to create:**
```
demo-bank/frontend/src/components/
├── VoiceButton.jsx
├── VoiceModal.jsx
├── TransferConfirmModal.jsx
└── PINInputModal.jsx
```

**Example:**
```javascript
// VoiceButton.jsx
import React, { useState } from 'react';
import AudioRecorderPlayer from 'react-native-audio-recorder-player';
import Tts from 'react-native-tts';
import { processVoiceAudio } from '../services/echobank';

const VoiceButton = ({ accountNumber, authToken }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [sessionId] = useState(`session_${Date.now()}`);
  const audioRecorderPlayer = new AudioRecorderPlayer();

  const startRecording = async () => {
    setIsRecording(true);
    await audioRecorderPlayer.startRecorder();
  };

  const stopRecording = async () => {
    const result = await audioRecorderPlayer.stopRecorder();
    setIsRecording(false);

    // Send to EchoBank
    const response = await processVoiceAudio(
      result,
      accountNumber,
      authToken,
      sessionId
    );

    // Speak response
    Tts.speak(response.response_text);

    // Handle action
    if (response.action === 'confirm_transfer') {
      showConfirmationModal(response.data);
    } else if (response.action === 'request_pin') {
      showPINInput();
    }
  };

  return (
    <button
      onMouseDown={startRecording}
      onMouseUp={stopRecording}
    >
      {isRecording ? '🎤 Listening...' : '🎤 Hold to Speak'}
    </button>
  );
};
```

**4.6 Transfer Screen (1.5 hours)**
- [ ] Select recipient (dropdown/list)
- [ ] Amount input
- [ ] Narration input (optional)
- [ ] Preview transfer details
- [ ] Confirm button → Ask for PIN → Execute

**Files to create:**
```
demo-bank/frontend/src/screens/TransferScreen.jsx
```

**4.7 Recipients Screen (1 hour)**
- [ ] List saved recipients
- [ ] Add recipient button
- [ ] Favorite toggle
- [ ] Delete recipient
- [ ] Search/filter

**Files to create:**
```
demo-bank/frontend/src/screens/RecipientsScreen.jsx
demo-bank/frontend/src/components/AddRecipientModal.jsx
```

**Testing:**
- [ ] Test login flow
- [ ] Test dashboard displays balance
- [ ] Test voice button records and sends audio
- [ ] Test TTS speaks responses
- [ ] Test complete voice transfer flow
- [ ] Test manual transfer (non-voice)

**Deliverable checklist:**
- [ ] User can login
- [ ] Dashboard shows balance and transactions
- [ ] Voice button works (records, sends, receives, speaks)
- [ ] Voice transfer completes successfully
- [ ] Manual transfer works
- [ ] Recipients can be added/deleted
- [ ] UI is premium/professional

---

## 🔄 Integration Testing

After all tasks are complete:

**Full Flow Test:**
1. Register user in Demo Bank app
2. Login to Demo Bank app
3. View balance on dashboard
4. Tap Voice button
5. Say: "Send five thousand naira to Sarah"
6. EchoBank transcribes and recognizes intent
7. Demo Bank API initiates transfer
8. App speaks: "You're about to send ₦5,000 to Sarah. Please confirm."
9. User says: "Confirm"
10. App speaks: "Please enter your PIN"
11. User enters PIN: 1234
12. Demo Bank verifies PIN
13. Paystack executes transfer
14. App speaks: "Transfer successful! Your new balance is ₦95,000"
15. Dashboard updates with new balance
16. Transaction appears in history

**Success Criteria:**
- ✅ Voice command initiates transfer
- ✅ Paystack transfer executes
- ✅ Balance updates
- ✅ Transaction recorded
- ✅ User receives voice confirmation

---

## ⏰ Timeline

**Day 1:**
- Developer A: Tasks 1.1-1.3 (Database + Models + Auth)
- Developer D: Tasks 4.1-4.2 (Project setup + API layer)

**Day 2:**
- Developer A: Tasks 1.4-1.6 (Accounts + Recipients + Transfers)
- Developer D: Tasks 4.3-4.4 (Login + Dashboard)

**Day 3:**
- Developer B: Tasks 2.1-2.2 (Paystack setup + Recipients)
- Developer C: Task 3.1 (Study EchoBank)
- Developer D: Task 4.5 (Voice button - CRITICAL)

**Day 4:**
- Developer B: Tasks 2.3-2.4 (Paystack transfers + Webhooks)
- Developer C: Tasks 3.2-3.4 (EchoBank integration)
- Developer D: Tasks 4.6-4.7 (Transfer + Recipients screens)

**Day 5:**
- All: Integration testing
- All: Bug fixes
- All: Polish UI/UX

**Total: 21-28 hours** (can be done in 3-5 days with 4 developers)

---

## 📦 Deliverables

1. **Demo Bank Backend** (Developer A + B)
   - PostgreSQL database with schema
   - FastAPI backend with all endpoints
   - Paystack integration for transfers
   - JWT authentication

2. **EchoBank Integration** (Developer C)
   - `DemoBankAPIClient` implementation
   - EchoBank configured to use Demo Bank
   - End-to-end voice flow tested

3. **Demo Bank Frontend** (Developer D)
   - Login + Dashboard screens
   - Voice button with TTS
   - Transfer + Recipients screens
   - Professional UI

4. **Documentation & Testing**
   - API test files (`.http`)
   - Integration test scenarios
   - User guide for demo

---

## 🎉 Success Metrics

At the end, you should be able to:
1. ✅ Login to Demo Bank app
2. ✅ See your balance
3. ✅ Tap voice button and say "Send money to Sarah"
4. ✅ Complete transfer via voice commands only
5. ✅ Transfer executes via Paystack
6. ✅ Balance updates
7. ✅ Receive voice confirmation

**This shows judges the complete integration story!**

---

## 📞 Coordination

**Daily standup questions:**
- What did I complete yesterday?
- What am I working on today?
- Any blockers?

**Communication:**
- Use GitHub Issues for bug tracking
- Use Discord/Slack for quick questions
- Share test data (accounts, PINs, Paystack keys)

**Shared Resources:**
- Test Paystack API keys (everyone uses same test account)
- Test user credentials (same test accounts for all)
- Database access (shared PostgreSQL instance or local + seed script)

---

**Ready to delegate! Share this with your team. 🚀**
