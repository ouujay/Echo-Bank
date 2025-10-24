# 🚀 Quick Start - Testing Your Work

## Prerequisites
- PostgreSQL installed and running
- Python 3.8+ installed

---

## 1️⃣ Setup Environment (5 minutes)

```bash
cd backend

# Create .env file
cp ../.env.example ../.env

# Edit .env - minimum required:
# DATABASE_URL=postgresql://your_user:your_password@localhost:5432/echobank
# JWT_SECRET_KEY=any_long_random_string
# ENCRYPTION_KEY=any_long_random_string
# (Set other values to "dummy" for testing)

# Install dependencies
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## 2️⃣ Setup Database (2 minutes)

```bash
# Create database
psql -U postgres -c "CREATE DATABASE echobank;"

# Create tables and test data
python scripts/setup_test_db.py
```

**You should see:**
```
✅ Test user created!
   Account: 0123456789
   PIN: 1234
   Balance: ₦100,000.00
✅ Created 4 test recipients
```

---

## 3️⃣ Start Server (1 minute)

```bash
uvicorn app.main:app --reload --port 8000
```

**Open in browser:** http://localhost:8000
**API Docs:** http://localhost:8000/docs

---

## 4️⃣ Run Tests (2 minutes)

### Option A: Automated Script (Recommended)

Open a **new terminal**:

```bash
cd backend
./scripts/test_api.sh
```

The script will walk you through all 12 tests interactively.

### Option B: Manual Testing

Open the detailed guide:
```bash
cat backend/TESTING_GUIDE.md
```

### Option C: Use API Docs

1. Go to http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"

---

## 🎯 Quick Test Examples

### Test 1: Search Recipient
```bash
curl "http://localhost:8000/api/v1/recipients/search?name=John" | jq
```

### Test 2: Initiate Transfer
```bash
curl -X POST "http://localhost:8000/api/v1/transfers/initiate" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": 1,
    "amount": 5000,
    "session_id": "test123"
  }' | jq
```

### Test 3: Verify PIN
```bash
# Replace YOUR_TRANSFER_ID with the ID from Test 2
curl -X POST "http://localhost:8000/api/v1/transfers/YOUR_TRANSFER_ID/verify-pin" \
  -H "Content-Type: application/json" \
  -d '{"pin": "1234"}' | jq
```

### Test 4: Confirm Transfer
```bash
curl -X POST "http://localhost:8000/api/v1/transfers/YOUR_TRANSFER_ID/confirm" \
  -H "Content-Type: application/json" \
  -d '{"confirmation": "confirm"}' | jq
```

---

## ✅ What You're Testing

1. **Recipients API** (6 endpoints)
   - Search by name (single/multiple/not found)
   - List all
   - Add new
   - Get by ID
   - Delete
   - Toggle favorite

2. **Transfers API** (5 endpoints)
   - Initiate transfer (with balance/limit checks)
   - Verify PIN (with lockout protection)
   - Confirm transfer (executes money movement)
   - Cancel transfer
   - Get transfer details

---

## 🐛 Troubleshooting

**Server won't start:**
```bash
# Check if port 8000 is already in use
lsof -ti:8000 | xargs kill -9
```

**Database connection error:**
```bash
# Check PostgreSQL is running
# macOS: brew services list | grep postgresql
# Ubuntu: sudo systemctl status postgresql
```

**ModuleNotFoundError:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📚 Full Documentation

- **Complete Testing Guide:** `backend/TESTING_GUIDE.md`
- **Developer Guide:** `DEVELOPER_GUIDE.md`
- **API Documentation:** http://localhost:8000/docs (when server is running)

---

## 🎉 Success Criteria

All these should work:
- ✅ Search for recipients (single, multiple, not found)
- ✅ Initiate transfers
- ✅ Balance validation (insufficient balance error)
- ✅ Daily limit validation (limit exceeded error)
- ✅ PIN verification (correct/incorrect)
- ✅ Transfer execution (balance deducted)
- ✅ Transfer cancellation

**If all tests pass, your Developer 2 work is complete! 🚀**
