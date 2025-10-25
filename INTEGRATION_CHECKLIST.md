# EchoBank + Demo Bank Integration Checklist

This document serves as a pre-flight checklist for Claude to verify before running or deploying the integrated system.

## 🔍 Pre-Run Checklist

### 1. CORS Configuration ✅
**Demo Bank Backend** must allow requests from:
- `http://localhost:3000` - Demo Bank Frontend (primary)
- `http://localhost:3001` - Demo Bank Frontend (alternate)
- `http://localhost:5173` - EchoBank Frontend (Vite default)
- `http://localhost:5174` - EchoBank Frontend (alternate)
- `http://localhost:8081` - Additional services
- `http://localhost:8000` - EchoBank API

**Location**: `backend/app/core/config.py`
```python
ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:5173,http://localhost:5174,http://localhost:8081,http://localhost:8000"
```

### 2. Service Ports ✅

| Service | Port | Status | URL |
|---------|------|--------|-----|
| **EchoBank API** | 8000 | Running | http://localhost:8000 |
| **Demo Bank API** | 8001 | Running | http://localhost:8001 |
| **Demo Bank Frontend** | 3000 | Running | http://localhost:3000 |
| **EchoBank Frontend** | 5173 | TBD | http://localhost:5173 |

### 3. Company Registration in EchoBank ✅

Demo Bank must be registered as a company in EchoBank:

- **Company ID**: 4
- **Company Name**: Demo Bank
- **Email**: demo@echobank.com
- **Status**: Active & Verified ✅
- **Base URL**: http://localhost:8001

**Verify Command**:
```bash
curl http://localhost:8000/api/v1/companies/4
```

### 4. API Endpoints Configuration ✅

EchoBank needs to know Demo Bank's endpoints:

```json
{
  "base_url": "http://localhost:8001",
  "auth_type": "bearer",
  "auth_header_name": "Authorization",
  "endpoints": {
    "get_balance": "/api/accounts/{account_number}/balance",
    "get_recipients": "/api/recipients",
    "initiate_transfer": "/api/transfers/initiate",
    "confirm_transfer": "/api/transfers/{transfer_id}/confirm",
    "verify_pin": "/api/transfers/{transfer_id}/verify-pin",
    "get_transactions": "/api/accounts/{account_id}/transactions",
    "add_recipient": "/api/recipients",
    "cancel_transfer": "/api/transfers/{transfer_id}/cancel"
  }
}
```

**Verify Command**:
```bash
curl http://localhost:8000/api/v1/companies/4/endpoints
```

### 5. Database Setup ✅

**Demo Bank Database**:
- Type: SQLite
- Location: `demo_bank.db` (root directory)
- Status: Created with tables ✅

**EchoBank Database**:
- Type: PostgreSQL
- URL: From `.env` file
- Companies table must have Demo Bank registered

### 6. Environment Variables

**Demo Bank** (`demo-bank/.env`):
```env
DATABASE_URL=sqlite:///demo_bank.db
JWT_SECRET_KEY=<secret>
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:5173,http://localhost:5174
ECHOBANK_API_URL=http://localhost:8000
```

**EchoBank** (`echobank/.env`):
```env
DATABASE_URL=postgresql://...
TOGETHER_API_KEY=<key>
WHISPERAPI=<key>
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:3000
```

### 7. Frontend API Configuration

**Demo Bank Frontend** (`frontend/src/services/api.ts`):
```typescript
const API_BASE_URL = 'http://localhost:8001/api';
```

**EchoBank Frontend** - Check configuration points to:
- EchoBank API: `http://localhost:8000`
- Demo Bank API (if direct): `http://localhost:8001`

## 🚀 Startup Sequence

### Step 1: Start Demo Bank Backend
```bash
cd demo-bank/backend
../venv/Scripts/uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Step 2: Start EchoBank Backend
```bash
cd echobank/backend
../venv/Scripts/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Start Demo Bank Frontend
```bash
cd demo-bank/frontend
npm run dev
# Should start on port 3000 (or 3001 if 3000 is taken)
```

### Step 4: Start EchoBank Frontend
```bash
cd echobank/frontend
npm run dev
# Should start on port 5173
```

## 🧪 Integration Test

Once all services are running, test the integration:

1. **Test Demo Bank API**:
```bash
curl http://localhost:8001/
# Should return: "Welcome to Demo Bank API"
```

2. **Test EchoBank API**:
```bash
curl http://localhost:8000/
# Should return EchoBank API info
```

3. **Test Company Registration**:
```bash
curl http://localhost:8000/api/v1/companies/4
# Should return Demo Bank details
```

4. **Test Voice Integration** (if ready):
```bash
curl -X POST "http://localhost:8000/api/v1/voice/process-text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Check my balance",
    "account_number": "5010598710",
    "company_id": 4,
    "token": "<user_token>"
  }'
```

## 📋 User Accounts

### Demo Bank Users

**Funbi** (Primary Test User):
- Email: funbi@demobank.ng
- Password: Funbi123
- PIN: 0000
- Account: 5010598710
- Balance: ₦100,000

**Adeleke**:
- Email: adeleke@demobank.ng
- Password: Password123
- PIN: 1111

**Therese**:
- Email: therese@demobank.ng
- Password: Password123
- PIN: 2222

## 🔧 Troubleshooting

### CORS Errors
- Check `ALLOWED_ORIGINS` in Demo Bank config
- Check `CORS_ORIGINS` in EchoBank config
- Ensure both include each other's frontend URLs

### Port Conflicts
- Demo Bank API: 8001 (not 8002, not 8000)
- EchoBank API: 8000
- Demo Bank Frontend: 3001 (not 3000 if taken)
- EchoBank Frontend: 5173

### Company Not Found
- Verify Demo Bank registered in EchoBank
- Check company ID is 4
- Ensure `is_active` and `is_verified` are true

### Endpoints Not Working
- Update endpoints configuration via:
```bash
curl -X POST "http://localhost:8000/api/v1/companies/4/endpoints" \
  -H "Content-Type: application/json" \
  -d @endpoints_config.json
```

## ✅ Completion Status

- [x] CORS configured in Demo Bank
- [x] Demo Bank registered in EchoBank (Company ID: 4)
- [x] API endpoints configured
- [x] Demo Bank API running on port 8001
- [x] EchoBank API running on port 8000
- [x] Demo Bank Frontend running on port 3001
- [x] User accounts created (Funbi)
- [ ] EchoBank Frontend running
- [ ] End-to-end voice integration tested
- [ ] Voice widget integrated in Demo Bank frontend

## 📝 Notes for Claude

When starting any service or running tests:

1. **Always check this checklist first**
2. **Verify all ports are correct**
3. **Confirm CORS settings include all necessary origins**
4. **Check company registration exists in EchoBank**
5. **Verify endpoints point to correct ports**
6. **Test basic connectivity before complex operations**

This checklist should be referenced at the start of every session to ensure proper integration setup.
