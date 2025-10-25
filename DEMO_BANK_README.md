# Demo Bank Application

A complete demo banking application showcasing EchoBank voice API integration with Paystack transfers.

## 🏗️ Architecture

```
demo-bank/
├── backend/               # FastAPI Backend
│   ├── app/
│   │   ├── models/       # SQLAlchemy models
│   │   ├── api/          # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── schemas/      # Pydantic schemas
│   │   └── core/         # Config, database, security
│   ├── venv/             # Python virtual environment
│   └── requirements.txt
│
└── frontend/             # React Web App
    ├── src/
    │   ├── pages/        # Login, Dashboard, Transfer, Recipients
    │   ├── components/   # Reusable UI components
    │   ├── services/     # API service layer
    │   ├── context/      # Auth context
    │   └── utils/        # Helper functions
    └── package.json
```

## 🚀 Running the Application

### Backend (Port 8002)
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8002
```

### Frontend (Port 3000)
```bash
cd frontend
npm start
```

## 📊 Database

**PostgreSQL Database:** `demo_bank`

**Test Accounts:**
- Email: testuser@demo.com
- Password: password123
- PIN: 1234
- Account: 0634250390
- Balance: ₦94,975.00

## 🎯 Features

### ✅ Completed
- User registration & authentication
- Account management
- Balance inquiry
- Transfer money (initiate → PIN → confirm)
- Recipient management
- Transaction history

### 🔜 Coming Next
- EchoBank voice integration
- Paystack real money transfers
- Mobile responsive UI

## 🔑 API Endpoints

**Base URL:** `http://localhost:8002/api`

### Authentication
- `POST /auth/register` - Create new user
- `POST /auth/login` - Login user
- `POST /auth/verify-pin` - Verify transaction PIN

### Accounts
- `GET /accounts` - List user accounts
- `GET /accounts/balance/{account_number}` - Get balance

### Transfers
- `POST /transfers/initiate` - Start transfer
- `POST /transfers/{id}/verify-pin` - Verify PIN
- `POST /transfers/{id}/confirm` - Execute transfer

### Recipients
- `GET /recipients` - List saved recipients
- `POST /recipients` - Add new recipient

## 🎨 Tech Stack

**Backend:**
- FastAPI (Python)
- SQLAlchemy + PostgreSQL
- JWT Authentication
- Bcrypt password hashing

**Frontend:**
- React + TypeScript
- Tailwind CSS
- React Router
- Axios
- Context API

## 📝 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://useruser@localhost:5432/demo_bank
SECRET_KEY=61d57af3db9ce80c5430a7df4f4a24145558cb0b7866397db285cf2839b5878f
PAYSTACK_SECRET_KEY=sk_test_1a8dbb9f6761fa90b5ad2eba4251fcbee0797d49
PAYSTACK_PUBLIC_KEY=pk_test_aab86ed9fb67cb51fa6b12813487b33874500ea2
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8002/api
```

## 🧪 Testing

Test the complete transfer flow:
1. Register/Login
2. View balance
3. Initiate transfer
4. Enter PIN
5. Confirm transfer
6. Check updated balance

---

**Built for 24-hour hackathon demo** 🚀
