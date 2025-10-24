# EchoBank API Testing Guide - Developer 2

This guide will walk you through testing all the **Transactions & Auth** features you built.

---

## 📋 Prerequisites

1. **PostgreSQL** installed and running
2. **Python 3.8+** installed
3. **.env file** configured

---

## Step 1: Setup Environment

### 1.1 Copy Environment Variables

```bash
cd backend
cp ../.env.example ../.env
```

### 1.2 Edit `.env` file

Update these critical values:

```bash
# Minimum required for testing
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/echobank

# Generate JWT secret (run this command):
# openssl rand -hex 32
JWT_SECRET_KEY=your_generated_secret_key

# Generate encryption key (run this command):
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your_generated_key

# For testing, you can use dummy values for these:
TOGETHER_API_KEY=dummy_key
WHISPERAPI=dummy_key
EMAIL_SENDER=test@test.com
EMAIL_PASSWORD=dummy
PAYSTACK_SECRET_KEY=dummy
PAYSTACK_PUBLIC_KEY=dummy
PAYSTACK_CALLBACK_URL=http://localhost:8000/callback
CLOUDINARY_CLOUD_NAME=dummy
CLOUDINARY_API_KEY=dummy
CLOUDINARY_API_SECRET=dummy
```

---

## Step 2: Install Dependencies

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 3: Setup Database

### 3.1 Create PostgreSQL Database

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE echobank;

# Exit
\q
```

### 3.2 Run Setup Script

```bash
# From backend directory
python scripts/setup_test_db.py
```

**Expected Output:**
```
============================================================
🏦 EchoBank - Database Setup Script
============================================================
🔧 Creating database tables...
✅ Tables created successfully!

👤 Creating test user...
✅ Test user created!
   Account: 0123456789
   Name: Test User
   Balance: ₦100,000.00
   PIN: 1234

📋 Creating test recipients...
✅ Created 4 test recipients:
   - John Okafor (Zenith Bank)
   - John Adeyemi (GTBank)
   - Mary Johnson (Access Bank)
   - David Brown (First Bank)

============================================================
🎉 Database setup complete!
============================================================

📝 Test Credentials:
   User ID: 1
   Account Number: 0123456789
   PIN: 1234
   Balance: ₦100,000.00
   Daily Limit: ₦50,000.00

🚀 You can now start testing the API!
```

---

## Step 4: Start Backend Server

```bash
# From backend directory
uvicorn app.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Open in browser:** http://localhost:8000

You should see:
```json
{
  "message": "EchoBank API",
  "status": "running",
  "version": "1.0.0"
}
```

**Check API docs:** http://localhost:8000/docs

---

## Step 5: Test Recipients API

Open a new terminal (keep the server running) and run these tests:

### Test 1: Search for Single Recipient

```bash
curl -X GET "http://localhost:8000/api/v1/recipients/search?name=Mary" | jq
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "recipients": [
      {
        "id": 3,
        "name": "Mary Johnson",
        "account_number": "0333333333",
        "bank_name": "Access Bank",
        "bank_code": "044"
      }
    ],
    "match_type": "single",
    "message": "Found Mary Johnson at Access Bank."
  }
}
```

✅ **Pass Criteria:** Returns 1 recipient with match_type "single"

---

### Test 2: Search for Multiple Recipients

```bash
curl -X GET "http://localhost:8000/api/v1/recipients/search?name=John" | jq
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "recipients": [
      {
        "id": 1,
        "name": "John Okafor",
        "account_number": "0111111111",
        "bank_name": "Zenith Bank"
      },
      {
        "id": 2,
        "name": "John Adeyemi",
        "account_number": "0222222222",
        "bank_name": "GTBank"
      }
    ],
    "match_type": "multiple",
    "message": "I found 2 matches. Say 1 for John Okafor or 2 for John Adeyemi."
  }
}
```

✅ **Pass Criteria:** Returns 2 recipients with match_type "multiple"

---

### Test 3: Search for Non-Existent Recipient

```bash
curl -X GET "http://localhost:8000/api/v1/recipients/search?name=NonExistent" | jq
```

**Expected Response (404):**
```json
{
  "detail": {
    "code": "RECIPIENT_NOT_FOUND",
    "message": "I couldn't find NonExistent in your contacts.",
    "suggestion": "Say 'add new' to add them."
  }
}
```

✅ **Pass Criteria:** Returns 404 with helpful error message

---

### Test 4: List All Recipients

```bash
curl -X GET "http://localhost:8000/api/v1/recipients" | jq
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "recipients": [
      {
        "id": 1,
        "name": "John Okafor",
        "account_number": "0111111111",
        "bank_name": "Zenith Bank",
        "bank_code": "057",
        "is_favorite": false
      }
      // ... more recipients
    ],
    "count": 4
  }
}
```

✅ **Pass Criteria:** Returns all 4 recipients

---

### Test 5: Add New Recipient

```bash
curl -X POST "http://localhost:8000/api/v1/recipients" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sarah Williams",
    "account_number": "0555555555",
    "bank_name": "UBA",
    "bank_code": "033",
    "is_favorite": false
  }' | jq
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "recipient": {
      "id": 5,
      "name": "Sarah Williams",
      "account_number": "0555555555",
      "bank_name": "UBA",
      "bank_code": "033",
      "is_favorite": false
    },
    "message": "✅ Sarah Williams added to your contacts."
  }
}
```

✅ **Pass Criteria:** Returns new recipient with ID

---

## Step 6: Test Transfers API

### Test 6: Initiate Transfer (Success)

```bash
curl -X POST "http://localhost:8000/api/v1/transfers/initiate" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": 1,
    "amount": 5000,
    "session_id": "test_session_123"
  }' | jq
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "transfer_id": "REF1234567890",
    "status": "pending_pin",
    "recipient": {
      "name": "John Okafor",
      "account_number": "0111111111",
      "bank_name": "Zenith Bank"
    },
    "amount": 5000.0,
    "currency": "NGN",
    "current_balance": 100000.0,
    "new_balance": 95000.0,
    "message": "Sending ₦5,000 to John Okafor. Please say your 4-digit PIN."
  }
}
```

✅ **Pass Criteria:**
- Returns transfer_id
- Status is "pending_pin"
- Shows correct balance calculations

**💡 Save the `transfer_id` for next tests!**

---

### Test 7: Initiate Transfer (Insufficient Balance)

```bash
curl -X POST "http://localhost:8000/api/v1/transfers/initiate" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": 1,
    "amount": 200000,
    "session_id": "test_session_124"
  }' | jq
```

**Expected Response (400):**
```json
{
  "detail": {
    "code": "INSUFFICIENT_BALANCE",
    "message": "Your balance is ₦100,000. You cannot send ₦200,000.",
    "current_balance": 100000.0,
    "requested_amount": 200000.0
  }
}
```

✅ **Pass Criteria:** Returns 400 with balance error

---

### Test 8: Initiate Transfer (Daily Limit Exceeded)

```bash
curl -X POST "http://localhost:8000/api/v1/transfers/initiate" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": 1,
    "amount": 60000,
    "session_id": "test_session_125"
  }' | jq
```

**Expected Response (400):**
```json
{
  "detail": {
    "code": "LIMIT_EXCEEDED",
    "message": "Your daily limit is ₦50,000. You've used ₦0.",
    "daily_limit": 50000.0,
    "used_amount": 0.0,
    "remaining": 50000.0,
    "suggestion": "Would you like to send ₦50,000 instead?"
  }
}
```

✅ **Pass Criteria:** Returns 400 with limit exceeded error

---

### Test 9: Verify PIN (Correct PIN)

**Replace `REF1234567890` with your actual transfer_id from Test 6:**

```bash
curl -X POST "http://localhost:8000/api/v1/transfers/REF1234567890/verify-pin" \
  -H "Content-Type: application/json" \
  -d '{
    "pin": "1234"
  }' | jq
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "transfer_id": "REF1234567890",
    "status": "pending_confirmation",
    "pin_verified": true,
    "message": "PIN verified. Say 'confirm' to complete the transfer."
  }
}
```

✅ **Pass Criteria:**
- Returns success
- Status changes to "pending_confirmation"

---

### Test 10: Verify PIN (Wrong PIN)

First, create a new transfer:

```bash
curl -X POST "http://localhost:8000/api/v1/transfers/initiate" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": 1,
    "amount": 3000,
    "session_id": "test_session_126"
  }' | jq
```

Then verify with wrong PIN:

```bash
curl -X POST "http://localhost:8000/api/v1/transfers/YOUR_TRANSFER_ID/verify-pin" \
  -H "Content-Type: application/json" \
  -d '{
    "pin": "9999"
  }' | jq
```

**Expected Response (401):**
```json
{
  "detail": {
    "code": "INVALID_PIN",
    "message": "Incorrect PIN. You have 2 attempts remaining.",
    "attempts_remaining": 2
  }
}
```

✅ **Pass Criteria:** Returns 401 with attempts remaining

---

### Test 11: Confirm Transfer

**Use the transfer_id from Test 9 (the one with verified PIN):**

```bash
curl -X POST "http://localhost:8000/api/v1/transfers/REF1234567890/confirm" \
  -H "Content-Type: application/json" \
  -d '{
    "confirmation": "confirm"
  }' | jq
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "transfer_id": "REF1234567890",
    "status": "completed",
    "recipient": {
      "name": "John Okafor",
      "account_number": "0111111111"
    },
    "amount": 5000.0,
    "transaction_ref": "REF1234567890",
    "timestamp": "2025-10-24T18:35:00",
    "new_balance": 95000.0,
    "message": "✅ Transfer successful! ₦5,000 sent to John Okafor. New balance: ₦95,000."
  }
}
```

✅ **Pass Criteria:**
- Status is "completed"
- Balance is deducted
- Success message shown

---

### Test 12: Cancel Transfer

Create a new transfer and cancel it:

```bash
# Create transfer
curl -X POST "http://localhost:8000/api/v1/transfers/initiate" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": 2,
    "amount": 2000,
    "session_id": "test_session_127"
  }' | jq

# Cancel it (use the returned transfer_id)
curl -X POST "http://localhost:8000/api/v1/transfers/YOUR_TRANSFER_ID/cancel" \
  -H "Content-Type: application/json" | jq
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "transfer_id": "REF...",
    "status": "cancelled",
    "message": "Transfer cancelled. No money was sent."
  }
}
```

✅ **Pass Criteria:** Transfer cancelled, no money deducted

---

## Step 7: Check Results in Database

```bash
psql -U postgres -d echobank

-- Check user balance
SELECT account_number, full_name, balance FROM users;

-- Check transactions
SELECT transaction_ref, amount, status, created_at FROM transactions ORDER BY created_at DESC;

-- Check recipients
SELECT name, bank_name, account_number FROM recipients;

\q
```

---

## ✅ Success Checklist

- [ ] Database tables created successfully
- [ ] Test user and recipients added
- [ ] Server starts without errors
- [ ] Can search for single recipient
- [ ] Can search for multiple recipients
- [ ] 404 error for non-existent recipient
- [ ] Can list all recipients
- [ ] Can add new recipient
- [ ] Can initiate transfer successfully
- [ ] Insufficient balance error works
- [ ] Daily limit check works
- [ ] PIN verification works (correct PIN)
- [ ] PIN verification fails (wrong PIN)
- [ ] Transfer confirmation executes successfully
- [ ] Balance is deducted after confirmation
- [ ] Can cancel pending transfer

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError"
```bash
# Make sure you're in the backend directory
cd backend
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### Error: "Connection refused" to database
```bash
# Check if PostgreSQL is running
# macOS:
brew services list | grep postgresql
# Ubuntu:
sudo systemctl status postgresql
```

### Error: "Table does not exist"
```bash
# Re-run the setup script
python scripts/setup_test_db.py
```

### Error: "401 Unauthorized" or JWT errors
For now, the API uses a test user (ID=1). JWT authentication will be added later by Developer 1.

---

## 🎉 Congratulations!

If all tests pass, you've successfully built:
- ✅ Complete database models
- ✅ PIN authentication with lockout
- ✅ Transfer validation (balance + limits)
- ✅ Transaction execution
- ✅ Recipient management
- ✅ 5 Transfer API endpoints
- ✅ 6 Recipient API endpoints

Your work as **Developer 2** is complete! 🚀
