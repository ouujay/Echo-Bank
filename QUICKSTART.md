# Demo Bank - Quick Start Guide

## 🎯 What We Built

A complete banking web application with:
- ✅ **Backend API** (FastAPI + PostgreSQL) - Running on port 8002
- ✅ **Frontend Web App** (React + TypeScript) - Will run on port 3000
- ✅ **Full Transfer Flow**: Initiate → PIN Verification → Confirm → Complete
- ✅ **Recipient Management**: Add, delete, favorite recipients
- ✅ **Transaction History**: View all past transfers
- ✅ **Authentication**: Register, Login with JWT tokens

## 🚀 Running the Application

### 1. Backend (Already Running!)
The backend is running on **http://localhost:8002**

- API Docs: http://localhost:8002/docs
- Health Check: http://localhost:8002/health

### 2. Frontend
```bash
cd frontend
npm run dev
```

The app will open at **http://localhost:3000**

## 🧪 Testing the Complete Flow

### Option 1: Use Existing Test User
```
Email: testuser@demo.com
Password: password123
PIN: 1234
Account: 0634250390
Balance: ₦94,975.00
```

### Option 2: Create New Account
1. Go to http://localhost:3000
2. Click "Register here"
3. Fill in the form:
   - Full Name: Your Name
   - Email: your@email.com
   - Phone: +2348123456789 or 08123456789
   - Password: password123
   - PIN: 1234
4. Click "Create Account"
5. You'll be auto-logged in with ₦100,000 starting balance!

## 📱 App Features & Testing

### 1. Dashboard
- View your balance
- See account number
- Recent transactions
- Quick actions (Transfer, Recipients, Refresh)

### 2. Transfer Money
**Complete Transfer Flow:**

1. **Click "Send Money"** on Dashboard
2. **Select Recipient** (you need to add one first if none exist)
3. **Enter Amount** (e.g., 5000) and optional narration
4. **Enter PIN** (1234 for test user)
5. **Confirm Transfer**
6. **Success!** Balance updates immediately

**To Test:**
```
1. Dashboard → Send Money
2. Go to Recipients → Add Recipient:
   - Name: Sarah Bello
   - Account: 0987654321
   - Bank: Demo Bank
3. Back to Transfer → Select Sarah → Amount: 5000
4. Enter PIN: 1234
5. Confirm → Transfer Complete!
```

### 3. Recipients Management
- **Add Recipients**: Click "+ Add Recipient"
- **Mark as Favorite**: Click ⭐ icon
- **Delete**: Click "Delete" button

### 4. Transaction History
- View all transactions on Dashboard
- Status badges (completed, pending, failed)
- Amount, date, reference number

## 🎨 What You'll See

### Login/Register Pages
- Beautiful gradient background
- Clean, modern forms
- Error handling with messages

### Dashboard
- Purple gradient balance card showing your balance
- Account number display
- Quick action cards
- Recent transactions list

### Transfer Page
- Step-by-step flow:
  1. Select recipient
  2. Enter amount & narration
  3. PIN verification (4-digit input)
  4. Confirmation screen
  5. Success message
- Beautiful success animation

### Recipients Page
- List of all saved recipients
- Add new recipients modal
- Toggle favorites
- Delete recipients

## 🔑 API Endpoints Being Used

**Authentication:**
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login
- `POST /api/auth/verify-pin` - Verify PIN

**Accounts:**
- `GET /api/accounts` - Get user accounts
- `GET /api/accounts/balance/{account_number}` - Get balance
- `GET /api/accounts/{id}/transactions` - Transaction history

**Recipients:**
- `GET /api/recipients` - List recipients
- `POST /api/recipients` - Add recipient
- `PUT /api/recipients/{id}/favorite` - Toggle favorite
- `DELETE /api/recipients/{id}` - Delete recipient

**Transfers:**
- `POST /api/transfers/initiate` - Start transfer
- `POST /api/transfers/{id}/verify-pin` - Verify PIN
- `POST /api/transfers/{id}/confirm` - Complete transfer
- `GET /api/transfers/{id}` - Get status

## 💡 Demo Script for Judges

1. **Show Registration** (30 sec)
   - Open http://localhost:3000
   - Click "Register"
   - Fill form → Auto-login with ₦100,000

2. **Show Dashboard** (30 sec)
   - Point out balance card
   - Show account number
   - Show transaction history

3. **Add Recipient** (45 sec)
   - Click "Recipients"
   - Add new recipient
   - Show it appears in list

4. **Complete Transfer** (90 sec)
   - Click "Send Money"
   - Select recipient
   - Enter amount: ₦10,000
   - Enter narration
   - Enter PIN: 1234
   - Confirm
   - **SHOW SUCCESS MESSAGE**
   - Go to Dashboard → **BALANCE UPDATED!**
   - **Transaction appears in history**

5. **Show Transaction History** (30 sec)
   - Scroll through transactions
   - Point out status, amount, date

**Total Demo Time: ~3-4 minutes**

## 🎯 Next Steps (After Basic App Works)

1. **EchoBank Voice Integration**
   - Add voice button to Dashboard
   - Connect to EchoBank API
   - Voice command: "Send 5000 to Sarah"
   - Complete transfer via voice

2. **Paystack Real Money Transfers**
   - Already have API keys in .env
   - Integrate Paystack API
   - Real money transfers (test mode)

3. **Polish & Deploy**
   - Add loading states
   - Better error handling
   - Deploy to Vercel/Azure

## 📊 Current Status

✅ **Backend API** - Fully functional, tested, running
✅ **Database** - PostgreSQL with all tables, seed data
✅ **Frontend** - Complete React app with all features
🔄 **Installation** - npm dependencies installing
⏳ **Testing** - Ready to test after npm install completes

## 🐛 Troubleshooting

**Port already in use:**
```bash
# Backend uses 8002, frontend uses 3000
# Change in vite.config.ts if needed
```

**Database connection error:**
```bash
# Check .env file has correct DATABASE_URL
# Verify PostgreSQL is running
```

**CORS error:**
```bash
# Already configured in backend for localhost:3000
# Check backend is running on port 8002
```

---

**You're almost ready to demo! Just waiting for npm install to finish** 🚀
