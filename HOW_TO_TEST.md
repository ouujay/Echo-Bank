# How to Test Paystack Integration

You have **3 ways** to test the complete Paystack integration:

---

## ⚡️ Quick Test (2 minutes) - **RECOMMENDED**

Run the automated test script:

```bash
cd /Users/useruser/Documents/demo-bank
./test_paystack.sh
```

**What it does:**
- ✅ Registers a test user
- ✅ Creates account with ₦100,000
- ✅ Adds recipient (triggers Paystack verification)
- ✅ Initiates ₦2,000 transfer
- ✅ Verifies PIN
- ✅ Confirms transfer (calls Paystack API)
- ✅ Checks updated balance
- ✅ Shows transaction history

**Look for:**
```
✨ Paystack recipient code generated!
🎉 Paystack Transfer Code: TRF_xyz123
```

**Then check backend logs for:**
```
INFO: Verifying account with Paystack
INFO: Paystack recipient created: RCP_xyz123
INFO: Initiating Paystack transfer
INFO: Paystack transfer initiated: TRF_abc456
```

---

## 📖 Manual Testing (30 minutes) - **COMPREHENSIVE**

Follow the detailed guide:

```bash
cat TESTING_GUIDE.md
```

**Covers:**
1. User Registration & Login
2. Check Balance & Account Details
3. Add Recipient with Paystack Verification
4. Complete Transfer with Paystack Integration
5. Paystack Dashboard Verification
6. Wallet Funding (Payment Collection)
7. Frontend Web App Testing
8. Error Handling & Edge Cases
9. API Documentation Check

**Use this for:**
- Thorough testing before demo
- Understanding each step
- Testing edge cases
- Manual verification

---

## 🖥️ Frontend Testing (5 minutes) - **VISUAL**

Test via the web app:

1. **Start frontend** (if not running):
   ```bash
   cd frontend
   npm run dev
   ```

2. **Open browser**: http://localhost:3000

3. **Login**:
   - Email: `testuser@demo.com`
   - Password: `password123`

4. **Add Recipient**:
   - Click "Recipients" → "+ Add Recipient"
   - Fill in details
   - Watch backend logs for Paystack calls

5. **Make Transfer**:
   - Click "Transfer"
   - Select recipient
   - Enter amount
   - Enter PIN: `1234`
   - Confirm
   - See success message with Paystack code!

6. **Check Paystack Dashboard**:
   - Go to https://dashboard.paystack.com/
   - See your transfers in TEST MODE

---

## 🔍 What to Verify

### ✅ Backend Logs
Watch terminal running backend for:
```
INFO: Verifying account 0123456789 with Paystack
INFO: Creating Paystack recipient for <Name>
INFO: Paystack recipient created: RCP_xyz123abc
INFO: Initiating Paystack transfer of ₦5000.0
INFO: Paystack transfer initiated: TRF_abc456def, status: pending
```

### ✅ Paystack Dashboard
1. Login to https://dashboard.paystack.com/
2. **Switch to TEST MODE** (toggle top right)
3. Check **Transfers** tab:
   - See your transfers
   - Transfer codes (TRF_xxx)
   - Amounts match your tests
4. Check **Recipients** tab:
   - See created recipients
   - Recipient codes (RCP_xxx)
   - Account numbers

### ✅ Database
```bash
# Check recipients have Paystack codes
psql -U useruser -d demo_bank -c "SELECT recipient_name, paystack_recipient_code FROM bank_recipients;"

# Check transactions have Paystack data
psql -U useruser -d demo_bank -c "SELECT transaction_ref, amount, paystack_transfer_code, status FROM bank_transactions ORDER BY id DESC LIMIT 5;"
```

### ✅ API Response
Transfer success message should include:
```
"Transfer of ₦5,000.00 to Sarah Bello successful! (Paystack: TRF_xyz123)"
```

---

## 🎯 Quick Verification Checklist

After testing, verify:

- [ ] Recipients in database have `paystack_recipient_code`
- [ ] Transactions have `paystack_transfer_code`
- [ ] Backend logs show Paystack API calls
- [ ] Transfers appear in Paystack dashboard
- [ ] Balances update correctly
- [ ] Frontend shows success with Paystack codes

---

## 🚨 Common Issues

### "Backend not running"
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8002
```

### "Paystack verification failed"
**Expected** for Demo Bank (code 999). For real banks (GTBank 058, etc.), you need valid test account numbers.

### "No Paystack code in response"
Check backend logs. If you see `paystack_status: "no_paystack_code"`, the API call failed (maybe rate limit) but transfer still completed in database.

---

## 📊 Test Results Summary

After successful test:

**Database:**
```
Recipients: 3+ with RCP_xxx codes
Transactions: 2+ with TRF_xxx codes
```

**Paystack Dashboard:**
```
Transfers: Visible in TEST MODE
Recipients: Created and listed
```

**Backend Logs:**
```
✅ Account verifications
✅ Recipient creations
✅ Transfer initiations
✅ All with Paystack API calls
```

---

## 🎉 Success = Ready for Demo!

If all tests pass:
- Your Paystack integration is **production-ready**
- All APIs are working correctly
- You can **confidently demo** to judges
- Ready to integrate **EchoBank voice assistant**

---

## 📝 For Judges

**Talking Points:**
1. "We use Paystack's real APIs in test mode"
2. "Every transfer appears in Paystack dashboard"
3. "Account verification uses Paystack Name Enquiry"
4. "Banks just swap the secret key to go live"

**Show Them:**
1. Make a transfer in the app
2. Open Paystack dashboard
3. Point to the same transfer
4. "This is production-ready code"

---

**Choose your testing method and get started!** 🚀

**Quick start:** `./test_paystack.sh`
**Detailed:** Read `TESTING_GUIDE.md`
**Visual:** Open http://localhost:3000
