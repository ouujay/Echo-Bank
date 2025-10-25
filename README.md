# 💳 Demo Bank - Paystack-Integrated Banking Application

A complete banking web application with **full Paystack integration** for real money transfers, account verification, and payment collection.

Built for EchoBank hackathon demo - production-ready code using Paystack APIs.

---

## 🎯 What This Is

A **fake bank backend** that uses **real Paystack APIs** to:
- ✅ Verify Nigerian bank accounts (Name Enquiry)
- ✅ Create transfer recipients on Paystack
- ✅ Send money via Paystack transfer rails
- ✅ Accept payments via Paystack checkout
- ✅ Track everything in Paystack dashboard

**All in Paystack TEST MODE** - no real money moves, but uses real APIs.

---

## 🚀 Quick Start

### 1. Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8002
```

**Backend runs on:** http://localhost:8002
**API Docs:** http://localhost:8002/docs

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

**Frontend runs on:** http://localhost:3000

### 3. Test Paystack Integration
```bash
# Automated test (2 minutes)
./test_paystack.sh

# OR manual test via browser
open http://localhost:3000
# Login: testuser@demo.com / password123
```

---

## 📚 Documentation

### Essential Guides

| Document | Purpose | Time |
|----------|---------|------|
| **[HOW_TO_TEST.md](HOW_TO_TEST.md)** | 3 ways to test (Quick/Manual/Visual) | 2-30 min |
| **[TESTING_GUIDE.md](TESTING_GUIDE.md)** | Complete step-by-step testing guide | 30 min |
| **[PAYSTACK_INTEGRATION.md](PAYSTACK_INTEGRATION.md)** | Technical details of integration | Reference |
| **[QUICKSTART.md](QUICKSTART.md)** | Original project quickstart | 5 min |

### Quick Links

- **Test Now:** Run `./test_paystack.sh`
- **API Docs:** http://localhost:8002/docs
- **Web App:** http://localhost:3000
- **Paystack Dashboard:** https://dashboard.paystack.com/

---

## 🎨 Features

### Authentication
- User registration with auto-account creation
- JWT-based login
- PIN verification with lockout protection
- Starting balance: ₦100,000

### Recipients Management
- Add recipients with **Paystack account verification**
- **Paystack Name Enquiry** for real account names
- Create **Paystack recipient codes** (RCP_xxx)
- Mark favorites
- Delete recipients

### Money Transfers
- Multi-step transfer flow (Initiate → PIN → Confirm)
- **Real Paystack transfer API calls**
- **Paystack transfer codes** (TRF_xxx)
- Transfer fees (₦10 or ₦25)
- Balance updates
- Transaction history
- **Appears in Paystack dashboard**

### Payment Collection
- Initialize payment sessions via Paystack
- Paystack checkout integration
- Payment verification
- Wallet funding
- **Real payment URLs** for user to complete

### Banking Operations
- Check balance
- View transaction history
- Account details
- Daily/monthly limits

---

## 🔧 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **Paystack API** - Payment rails integration
- **JWT** - Authentication
- **bcrypt** - Password/PIN hashing

### Frontend
- **React** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Axios** - HTTP client
- **React Router** - Routing

### Integration
- **Paystack Test Mode** - All APIs in test environment
- **Real API calls** - Not mocked, actual Paystack
- **Webhook-ready** - Architecture supports real-time updates

---

## 📊 Project Structure

```
demo-bank/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── accounts.py
│   │   │   ├── recipients.py
│   │   │   ├── transfers.py
│   │   │   └── payments.py
│   │   ├── services/     # Business logic
│   │   │   ├── auth.py
│   │   │   ├── account.py
│   │   │   ├── recipient.py
│   │   │   ├── transfer.py
│   │   │   ├── payment.py
│   │   │   └── paystack.py  # ⭐ Paystack integration
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── core/         # Config, security, database
│   ├── .env              # Environment variables
│   └── venv/             # Python virtual environment
├── frontend/
│   ├── src/
│   │   ├── pages/        # React pages
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Transfer.tsx
│   │   │   └── Recipients.tsx
│   │   ├── services/     # API client
│   │   │   └── api.ts
│   │   ├── context/      # React context
│   │   └── App.tsx
│   └── package.json
├── test_paystack.sh      # ⭐ Automated test script
├── HOW_TO_TEST.md        # ⭐ Testing guide
├── TESTING_GUIDE.md      # ⭐ Detailed testing
├── PAYSTACK_INTEGRATION.md # ⭐ Technical docs
└── README.md             # This file
```

---

## 🔑 Environment Variables

```bash
# Backend (.env)
DATABASE_URL=postgresql://useruser@localhost:5432/demo_bank
PAYSTACK_SECRET_KEY=sk_test_1a8dbb9f6761fa90b5ad2eba4251fcbee0797d49
PAYSTACK_PUBLIC_KEY=pk_test_YOUR_KEY
PAYSTACK_BASE_URL=https://api.paystack.co
SECRET_KEY=61d57af3db9ce80c5430a7df4f4a24145558cb0b7866397db285cf2839b5878f
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8002
```

---

## 🧪 Testing Options

### Option 1: Quick Automated Test ⚡️ (2 minutes)
```bash
./test_paystack.sh
```

**What it does:**
- Registers user
- Adds recipient with Paystack
- Makes transfer via Paystack
- Verifies everything works

**Look for:**
```
✨ Paystack recipient code generated!
🎉 Paystack Transfer Code: TRF_xyz123
```

### Option 2: Manual Testing 📖 (30 minutes)
```bash
cat TESTING_GUIDE.md
```

**Complete guide with:**
- Step-by-step cURL commands
- Expected responses
- Verification steps
- Edge cases
- Paystack dashboard checks

### Option 3: Frontend Testing 🖥️ (5 minutes)
```bash
# Open browser
open http://localhost:3000

# Login with test user
Email: testuser@demo.com
Password: password123
PIN: 1234

# Make a transfer and watch it appear in Paystack!
```

---

## 📱 API Endpoints

### Authentication
```
POST /api/auth/register      # Create account
POST /api/auth/login         # Login
POST /api/auth/verify-pin    # Verify PIN
```

### Accounts
```
GET  /api/accounts                        # Get user accounts
GET  /api/accounts/balance/{account_num}  # Check balance
GET  /api/accounts/{id}/transactions      # Transaction history
```

### Recipients
```
GET    /api/recipients           # List recipients
POST   /api/recipients           # Add recipient (→ Paystack)
PUT    /api/recipients/{id}/favorite  # Toggle favorite
DELETE /api/recipients/{id}      # Delete recipient
```

### Transfers
```
POST /api/transfers/initiate          # Start transfer
POST /api/transfers/{id}/verify-pin   # Verify PIN
POST /api/transfers/{id}/confirm      # Execute (→ Paystack)
GET  /api/transfers/{id}              # Check status
```

### Payments ⭐ NEW
```
POST /api/payments/fund-wallet   # Initialize payment (→ Paystack)
POST /api/payments/verify        # Verify payment (→ Paystack)
GET  /api/payments/callback      # Payment callback
```

---

## 🎯 Paystack Integration Details

### What's Integrated

1. **Account Verification** (`/bank/resolve`)
   - Verifies account numbers
   - Returns real account names
   - Used when adding recipients

2. **Transfer Recipients** (`/transferrecipient`)
   - Creates Paystack recipients
   - Generates RCP_xxx codes
   - Stored in database

3. **Money Transfers** (`/transfer`)
   - Initiates real Paystack transfers
   - Returns TRF_xxx codes
   - Tracks status

4. **Transfer Verification** (`/transfer/verify/{code}`)
   - Checks transfer status
   - Confirms completion

5. **Payment Initialization** (`/transaction/initialize`)
   - Creates payment sessions
   - Returns checkout URL
   - For wallet funding

6. **Payment Verification** (`/transaction/verify/{ref}`)
   - Confirms payment success
   - Credits wallet

### How Transfers Work

```
User adds recipient
    ↓
Paystack verifies account (Name Enquiry)
    ↓
Paystack creates recipient (RCP_xxx)
    ↓
User initiates transfer
    ↓
User enters PIN
    ↓
User confirms
    ↓
Backend calls Paystack transfer API
    ↓
Paystack returns TRF_xxx code
    ↓
Transfer appears in Paystack dashboard
    ↓
Balance updated in database
```

---

## 🏗️ Database Schema

```sql
-- Users
bank_users (id, email, phone, full_name, password_hash, pin_hash, ...)

-- Accounts
bank_accounts (id, user_id, account_number, balance, ...)

-- Recipients
bank_recipients (
    id,
    user_id,
    recipient_name,
    account_number,
    bank_code,
    paystack_recipient_code,  -- RCP_xxx from Paystack
    is_verified,
    ...
)

-- Transactions
bank_transactions (
    id,
    account_id,
    transaction_ref,
    amount,
    fee,
    recipient_id,
    status,
    paystack_transfer_code,  -- TRF_xxx from Paystack
    paystack_status,
    ...
)
```

---

## 🎓 For Judges / Demo

### Pitch Points

1. **"Production-ready Paystack integration"**
   - Using real Paystack APIs in test mode
   - Not mocked or simulated
   - Same code works in production

2. **"Everything appears in Paystack dashboard"**
   - Show transfer in app
   - Open Paystack dashboard
   - Point to same transfer
   - "This is real integration"

3. **"Banks just swap the secret key"**
   - Change `PAYSTACK_SECRET_KEY` to production
   - No code changes needed
   - Ready to handle real money

4. **"Built for voice banking"**
   - Clean API for EchoBank integration
   - All Paystack complexity handled
   - Voice assistant just calls endpoints

### Demo Script (3 minutes)

1. **Show Dashboard** (30s)
   - "User has ₦100,000 balance"

2. **Add Recipient** (30s)
   - Add recipient via UI
   - "Paystack verifies the account"
   - Show RCP_xxx code in logs

3. **Make Transfer** (60s)
   - Select recipient
   - Enter amount
   - Enter PIN
   - Confirm
   - "Transfer goes through Paystack"
   - Show success with TRF_xxx code

4. **Show Paystack Dashboard** (60s)
   - Open https://dashboard.paystack.com/
   - Navigate to Transfers
   - Point to the transfer just made
   - "Same transaction, real Paystack APIs"

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check PostgreSQL is running
psql -U useruser -d demo_bank

# Check port 8002 is free
lsof -i :8002

# Reinstall dependencies
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Paystack not showing transfers
- Check you're in **TEST MODE** (toggle in Paystack dashboard)
- Check backend logs for Paystack API calls
- Verify `PAYSTACK_SECRET_KEY` is correct in `.env`
- Demo Bank (999) won't show in Paystack (use real bank codes)

### Database errors
```bash
# Reset database
psql -U useruser -d demo_bank -f backend/init_demo_bank.sql
```

---

## 📞 Support

- **Documentation:** See files in this directory
- **API Docs:** http://localhost:8002/docs
- **Paystack Docs:** https://paystack.com/docs/
- **Test Script:** `./test_paystack.sh`

---

## 🚀 Next Steps

1. **Test the integration** → `./test_paystack.sh`
2. **Check Paystack dashboard** → Verify transfers appear
3. **Try the web app** → http://localhost:3000
4. **Integrate EchoBank** → Voice assistant ready to connect!

---

## ✅ Status

- ✅ Backend API - **Running**
- ✅ Frontend App - **Running**
- ✅ Paystack Integration - **Complete**
- ✅ Database - **Configured**
- ✅ Testing - **Automated + Manual**
- ✅ Documentation - **Complete**
- 🔄 EchoBank Integration - **Ready to start**

---

## 📄 License

Built for EchoBank Hackathon Demo - October 2025

---

**🎉 You're ready to demo Paystack-integrated banking!**

Start with: `./test_paystack.sh` or `open http://localhost:3000`
