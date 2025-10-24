# Demo Bank App - Database Schema & Architecture

## Overview

This is the database schema for a **Demo Bank Application** that integrates with EchoBank Voice API.
The demo bank simulates a real Nigerian bank (like GTBank, Zenith) and uses Paystack for transfers.

**Purpose:**
- Show judges how a real bank integrates EchoBank
- Use Paystack for actual money transfers
- Complete demonstration: Bank App → EchoBank Voice → Paystack Transfers

---

## Database: `demo_bank`

### Table: `bank_users`
Customer accounts in the demo bank.

```sql
CREATE TABLE bank_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    bvn VARCHAR(11),  -- Bank Verification Number (Nigerian ID)
    password_hash VARCHAR(255) NOT NULL,
    pin_hash VARCHAR(255) NOT NULL,  -- 4-digit transaction PIN
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    pin_attempts INTEGER DEFAULT 0,
    pin_locked_until TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_bank_users_email ON bank_users(email);
CREATE INDEX idx_bank_users_phone ON bank_users(phone);
```

**Sample Data:**
```
id: 1
email: john.doe@email.com
phone: +2348012345678
full_name: John Doe
bvn: 12345678901
pin: 1234 (hashed)
```

---

### Table: `bank_accounts`
Bank accounts (users can have multiple accounts: savings, current).

```sql
CREATE TABLE bank_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES bank_users(id) ON DELETE CASCADE,
    account_number VARCHAR(10) UNIQUE NOT NULL,  -- NUBAN format
    account_name VARCHAR(255) NOT NULL,  -- Account holder name
    account_type VARCHAR(20) DEFAULT 'savings',  -- savings, current
    balance NUMERIC(15, 2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'NGN',
    daily_transfer_limit NUMERIC(15, 2) DEFAULT 50000.00,  -- ₦50,000
    monthly_transfer_limit NUMERIC(15, 2) DEFAULT 500000.00,  -- ₦500,000
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_bank_accounts_user_id ON bank_accounts(user_id);
CREATE UNIQUE INDEX idx_bank_accounts_number ON bank_accounts(account_number);
```

**Sample Data:**
```
id: 1
user_id: 1
account_number: 0123456789
account_name: John Doe
balance: 100000.00
daily_transfer_limit: 50000.00
```

---

### Table: `bank_recipients`
Saved beneficiaries for quick transfers.

```sql
CREATE TABLE bank_recipients (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES bank_users(id) ON DELETE CASCADE,
    recipient_name VARCHAR(255) NOT NULL,
    account_number VARCHAR(10) NOT NULL,
    bank_name VARCHAR(100) NOT NULL,
    bank_code VARCHAR(10) NOT NULL,  -- Nigerian bank code (e.g., 058 for GTBank)
    paystack_recipient_code VARCHAR(100),  -- Paystack transfer recipient code
    is_favorite BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,  -- Verified via Paystack name enquiry
    last_transfer_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_bank_recipients_user_id ON bank_recipients(user_id);
CREATE INDEX idx_bank_recipients_favorite ON bank_recipients(user_id, is_favorite);
```

**Sample Data:**
```
id: 1
user_id: 1
recipient_name: Sarah Bello
account_number: 0987654321
bank_name: GTBank
bank_code: 058
paystack_recipient_code: RCP_abc123xyz
is_favorite: true
```

---

### Table: `bank_transactions`
All transfers and transactions.

```sql
CREATE TABLE bank_transactions (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES bank_accounts(id),
    transaction_ref VARCHAR(50) UNIQUE NOT NULL,  -- Internal reference
    transaction_type VARCHAR(20) NOT NULL,  -- debit, credit, transfer
    amount NUMERIC(15, 2) NOT NULL,
    fee NUMERIC(10, 2) DEFAULT 0.00,  -- Transfer fee
    currency VARCHAR(3) DEFAULT 'NGN',

    -- For transfers
    recipient_id INTEGER REFERENCES bank_recipients(id),
    recipient_account VARCHAR(10),
    recipient_name VARCHAR(255),
    recipient_bank_name VARCHAR(100),
    recipient_bank_code VARCHAR(10),

    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending',  -- pending_pin, pending_confirmation, processing, completed, failed, cancelled
    narration TEXT,

    -- Paystack integration
    paystack_transfer_code VARCHAR(100),  -- Paystack transfer reference
    paystack_transfer_id VARCHAR(100),
    paystack_status VARCHAR(50),

    -- Timestamps
    initiated_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    failed_at TIMESTAMP NULL,

    -- Failure tracking
    failure_reason TEXT,

    -- Voice/session tracking
    session_id VARCHAR(100),  -- Links to EchoBank session
    initiated_via VARCHAR(20) DEFAULT 'app',  -- app, voice, ussd, web

    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_bank_transactions_account_id ON bank_transactions(account_id);
CREATE INDEX idx_bank_transactions_status ON bank_transactions(status);
CREATE INDEX idx_bank_transactions_ref ON bank_transactions(transaction_ref);
CREATE INDEX idx_bank_transactions_paystack ON bank_transactions(paystack_transfer_code);
CREATE INDEX idx_bank_transactions_date ON bank_transactions(created_at DESC);
```

**Sample Data:**
```
id: 1
account_id: 1
transaction_ref: TXN20251024123456
transaction_type: transfer
amount: 5000.00
fee: 10.00
recipient_account: 0987654321
recipient_name: Sarah Bello
status: completed
paystack_transfer_code: TRF_xyz789
initiated_via: voice
session_id: echobank_session_001
```

---

### Table: `paystack_transfers`
Paystack-specific transfer tracking (for reconciliation).

```sql
CREATE TABLE paystack_transfers (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES bank_transactions(id),
    transfer_code VARCHAR(100) UNIQUE NOT NULL,  -- Paystack transfer code
    transfer_id VARCHAR(100),  -- Paystack transfer ID
    recipient_code VARCHAR(100),  -- Paystack recipient code
    amount NUMERIC(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'NGN',
    status VARCHAR(50),  -- pending, success, failed, reversed
    reason TEXT,  -- Transfer description

    -- Paystack response data
    paystack_response JSONB,  -- Full Paystack API response

    -- Webhook tracking
    webhook_received BOOLEAN DEFAULT FALSE,
    webhook_at TIMESTAMP NULL,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_paystack_transfers_transaction_id ON paystack_transfers(transaction_id);
CREATE UNIQUE INDEX idx_paystack_transfers_code ON paystack_transfers(transfer_code);
```

---

### Table: `daily_transfer_limits`
Track daily transfer totals per account.

```sql
CREATE TABLE daily_transfer_limits (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES bank_accounts(id),
    transfer_date DATE NOT NULL,
    total_amount NUMERIC(15, 2) DEFAULT 0.00,
    transfer_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW(),

    UNIQUE(account_id, transfer_date)
);

-- Indexes
CREATE INDEX idx_daily_limits_account_date ON daily_transfer_limits(account_id, transfer_date);
```

---

### Table: `auth_tokens`
JWT tokens for authentication.

```sql
CREATE TABLE auth_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES bank_users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    device_id VARCHAR(255),
    device_name VARCHAR(255),
    ip_address VARCHAR(50),
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_auth_tokens_user_id ON auth_tokens(user_id);
CREATE INDEX idx_auth_tokens_token ON auth_tokens(token_hash);
CREATE INDEX idx_auth_tokens_expires ON auth_tokens(expires_at);
```

---

## Database Relationships

```
bank_users (1) ─────── (N) bank_accounts
                       (N) bank_recipients
                       (N) auth_tokens

bank_accounts (1) ──── (N) bank_transactions

bank_recipients (1) ── (N) bank_transactions

bank_transactions (1) ─ (1) paystack_transfers
```

---

## Paystack Integration Schema

### Paystack Recipient Object
When adding a new beneficiary, create a Paystack recipient:

```json
{
  "type": "nuban",
  "name": "Sarah Bello",
  "account_number": "0987654321",
  "bank_code": "058",
  "currency": "NGN"
}
```

Store returned `recipient_code` in `bank_recipients.paystack_recipient_code`.

### Paystack Transfer Object
When initiating transfer:

```json
{
  "source": "balance",
  "amount": 500000,  // Amount in kobo (₦5,000.00 = 500000 kobo)
  "recipient": "RCP_abc123xyz",
  "reason": "Transfer to Sarah Bello",
  "currency": "NGN"
}
```

Store returned `transfer_code` in `bank_transactions.paystack_transfer_code`.

---

## Demo Bank API Endpoints

### Authentication
- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - Login (returns JWT)
- `POST /api/auth/verify-pin` - Verify transaction PIN
- `POST /api/auth/logout` - Revoke token

### Accounts
- `GET /api/accounts` - Get user's accounts
- `GET /api/accounts/{account_id}/balance` - Get balance
- `GET /api/accounts/{account_id}/transactions` - Transaction history

### Recipients
- `GET /api/recipients` - Get saved recipients
- `POST /api/recipients` - Add new recipient (creates Paystack recipient)
- `POST /api/recipients/verify` - Verify account via Paystack name enquiry
- `PUT /api/recipients/{id}/favorite` - Toggle favorite
- `DELETE /api/recipients/{id}` - Remove recipient

### Transfers
- `POST /api/transfers/initiate` - Start transfer (check limits, create pending)
- `POST /api/transfers/{id}/verify-pin` - Verify PIN
- `POST /api/transfers/{id}/confirm` - Execute via Paystack
- `GET /api/transfers/{id}` - Get transfer status
- `POST /api/transfers/{id}/cancel` - Cancel pending transfer

### Paystack Webhooks
- `POST /api/webhooks/paystack` - Receive Paystack transfer updates

---

## EchoBank Integration Points

The Demo Bank implements `BankAPIClient` interface to connect with EchoBank:

```python
# demo_bank/integrations/echobank_adapter.py

class DemoBankAPIClient(BankAPIClient):
    """
    Demo Bank's implementation of EchoBank interface.
    Routes EchoBank requests to Demo Bank's API.
    """

    async def verify_account(self, account_number: str, pin: str) -> Dict:
        # Call: POST /api/auth/verify-pin
        pass

    async def get_balance(self, account_number: str, token: str) -> Dict:
        # Call: GET /api/accounts/{account_id}/balance
        pass

    async def initiate_transfer(...) -> Dict:
        # Call: POST /api/transfers/initiate
        pass

    # ... implement all BankAPIClient methods
```

---

## Sample Data for Demo

### Test User 1
```sql
INSERT INTO bank_users (email, phone, full_name, password_hash, pin_hash)
VALUES ('john@demo.com', '+2348012345678', 'John Doe', '<bcrypt_hash>', '<bcrypt_1234>');

INSERT INTO bank_accounts (user_id, account_number, account_name, balance)
VALUES (1, '0123456789', 'John Doe', 100000.00);
```

### Test User 2
```sql
INSERT INTO bank_users (email, phone, full_name, password_hash, pin_hash)
VALUES ('sarah@demo.com', '+2348087654321', 'Sarah Bello', '<bcrypt_hash>', '<bcrypt_5678>');

INSERT INTO bank_accounts (user_id, account_number, account_name, balance)
VALUES (2, '0987654321', 'Sarah Bello', 50000.00);
```

### Test Recipients
```sql
INSERT INTO bank_recipients (user_id, recipient_name, account_number, bank_name, bank_code, paystack_recipient_code, is_favorite)
VALUES
(1, 'Sarah Bello', '0987654321', 'GTBank', '058', 'RCP_test123', TRUE),
(1, 'Mary Johnson', '0111222333', 'Access Bank', '044', 'RCP_test456', FALSE);
```

---

## Tech Stack for Demo Bank

### Backend
- **FastAPI** (Python) - REST API
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **Paystack Python SDK** - Payments
- **JWT** - Authentication
- **Bcrypt** - Password hashing

### Frontend
- **React** or **React Native** - Mobile app
- **Redux/Context** - State management
- **Axios** - API calls
- **react-native-audio-recorder-player** - Voice recording
- **Web Speech API / react-native-tts** - Text-to-speech

### Deployment
- **Azure Web App** - Backend API
- **Azure Database for PostgreSQL** - Database
- **Vercel / Azure Static Web Apps** - Frontend

---

## Project Structure

```
demo-bank/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── account.py
│   │   │   ├── recipient.py
│   │   │   ├── transaction.py
│   │   │   └── paystack_transfer.py
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── accounts.py
│   │   │   ├── recipients.py
│   │   │   ├── transfers.py
│   │   │   └── webhooks.py
│   │   ├── services/
│   │   │   ├── paystack.py  # Paystack integration
│   │   │   ├── transfer.py  # Transfer logic
│   │   │   └── auth.py      # JWT auth
│   │   ├── integrations/
│   │   │   └── echobank_adapter.py  # BankAPIClient implementation
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── screens/
│   │   │   ├── LoginScreen.jsx
│   │   │   ├── DashboardScreen.jsx
│   │   │   ├── TransferScreen.jsx
│   │   │   └── RecipientsScreen.jsx
│   │   ├── components/
│   │   │   ├── VoiceButton.jsx  # EchoBank integration
│   │   │   ├── TransferModal.jsx
│   │   │   └── PINInput.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── auth.js
│   │   │   └── echobank.js  # EchoBank Voice API client
│   │   └── App.jsx
│   ├── package.json
│   └── .env
└── init_demo_bank.sql  # Database initialization
```

---

## Task Allocation

### Task 1: Demo Bank Backend (Developer A)
**Time:** 6-8 hours

**Deliverables:**
- Database schema implementation
- User authentication (JWT)
- Account management endpoints
- Recipient management endpoints
- Transfer endpoints (WITHOUT Paystack first)
- Basic validation and error handling

**Files to create:**
- All backend models
- All API endpoints
- Database initialization script

---

### Task 2: Paystack Integration (Developer B)
**Time:** 4-6 hours

**Deliverables:**
- Paystack service for transfers
- Paystack recipient creation
- Name enquiry (account verification)
- Webhook handling for transfer status
- Transfer reconciliation

**Files to create:**
- `services/paystack.py`
- `api/webhooks.py`
- Update transfer endpoints to use Paystack

---

### Task 3: EchoBank Integration (Developer C)
**Time:** 3-4 hours

**Deliverables:**
- Implement `DemoBankAPIClient` (BankAPIClient interface)
- Connect EchoBank voice endpoints to Demo Bank API
- Test voice-to-transfer flow
- Update EchoBank config to use Demo Bank adapter

**Files to create:**
- `demo_bank/integrations/echobank_adapter.py`
- Update EchoBank to use this adapter instead of MockBankAPI

---

### Task 4: Demo Bank Frontend (Developer D)
**Time:** 8-10 hours

**Deliverables:**
- Login screen
- Dashboard (balance, recent transactions)
- Transfer screen
- Recipients screen
- **Voice button** (integrates with EchoBank)
- TTS for speaking responses

**Files to create:**
- All frontend screens and components
- EchoBank voice integration
- API service layer

---

## Testing Strategy

1. **Unit Tests**: Each endpoint, each Paystack function
2. **Integration Tests**: Complete transfer flow
3. **Voice Tests**: Voice command → Transfer completion
4. **Paystack Tests**: Use Paystack test mode API keys
5. **End-to-End**: Login → Voice "Send 5000 to Sarah" → Transfer completes

---

## Deployment Checklist

- [ ] Create `demo_bank` PostgreSQL database
- [ ] Run `init_demo_bank.sql` for schema
- [ ] Insert test users and accounts
- [ ] Set Paystack API keys (test mode)
- [ ] Deploy Demo Bank backend to Azure
- [ ] Configure EchoBank to use `DemoBankAPIClient`
- [ ] Deploy Demo Bank frontend
- [ ] Test complete voice flow

---

## Success Criteria

✅ User can login to Demo Bank app
✅ User can see balance
✅ User can add recipient (creates Paystack recipient)
✅ User can tap voice button and say "Send 5000 to Sarah"
✅ EchoBank recognizes intent
✅ Demo Bank initiates transfer via Paystack
✅ Transfer completes successfully
✅ User receives voice confirmation
✅ Balance updates
✅ Transaction appears in history

**Result:** Complete demonstration of Bank App + EchoBank + Paystack integration!

---

## Notes

- Use **Paystack Test Mode** for demo (no real money)
- Test account numbers: Paystack provides test accounts
- Daily limit enforcement to prevent overspending
- PIN verification before every transfer
- Webhook reconciliation for Paystack status updates
- Session management via EchoBank for voice conversations

---

**This demo shows judges exactly how any Nigerian bank can integrate EchoBank in days!**
