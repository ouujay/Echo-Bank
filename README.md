# EchoBank - Voice-Powered Banking Assistant

> Empowering inclusive banking through natural voice interactions for visually impaired, elderly, and low-literacy users in Nigeria.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.0-61DAFB.svg)](https://reactjs.org)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg)](https://python.org)

---

## 🎯 Overview

**EchoBank** is an enterprise-grade voice banking assistant designed to be embedded within existing bank mobile applications. It enables users to perform financial transactions naturally through conversation, leveraging cutting-edge AI technologies including Whisper for speech-to-text and LLMs for intent recognition.

### Key Features

- 🎤 **Natural Voice Interface** - Speak naturally in Nigerian English
- 🔒 **Bank-Grade Security** - Voice PIN + JWT authentication + device binding
- 🚀 **Smart Conversation Flow** - Context-aware with intelligent interrupts
- 💸 **Full Transaction Support** - Send money, check balance, manage recipients
- ♿ **Accessibility First** - Designed for visually impaired and elderly users
- 🌍 **Scalable Architecture** - Deploy on Azure Web Apps, supports 52M+ users

---

## 🏗️ Architecture

```
┌─────────────────┐
│   React UI      │  ← Voice interface with TTS
│  (Frontend)     │
└────────┬────────┘
         │
    ┌────▼────────────┐
    │   FastAPI       │  ← Core state machine
    │   (Backend)     │
    └────┬────────────┘
         │
    ┌────▼─────────────────────┐
    │  AI Services             │
    │  • Whisper (STT)         │
    │  • Together AI / GPT     │
    │  • Intent Recognition    │
    └────┬─────────────────────┘
         │
    ┌────▼─────────────────────┐
    │  Bank Integration        │
    │  • Zenith Bank API       │
    │  • Paystack Payments     │
    └──────────────────────────┘
```

---

## 📦 Tech Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL (Azure-compatible / Supabase ready)
- **AI Services**: OpenAI Whisper, Together AI
- **Authentication**: JWT + Voice PIN
- **Payment**: Paystack Integration
- **Storage**: Cloudinary for media

### Frontend
- **Framework**: React 18 + Vite
- **Styling**: Modular CSS
- **Build Tool**: Vite 7.x
- **Voice**: Web Speech API + TTS

### Deployment
- **Hosting**: Azure Web Apps (recommended)
- **Database**: Supabase / Azure PostgreSQL
- **Session**: In-memory (single instance) / Azure Cache for Redis (multi-instance)

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL** (or Supabase account)
- API Keys for:
  - Together AI / OpenAI
  - Paystack
  - Cloudinary (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ouujay/Echo-Bank.git
   cd Echo-Bank
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database credentials
   ```

3. **Backend Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate

   # Install dependencies
   cd backend
   pip install -r requirements.txt
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

5. **Database Setup**
   ```bash
   # Create database
   psql -U postgres
   CREATE DATABASE echobank;
   \q

   # Run migrations (when available)
   cd backend
   alembic upgrade head
   ```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access the application:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📋 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `TOGETHER_API_KEY` | Together AI API key | ✅ |
| `WHISPERAPI` | OpenAI API key (for Whisper) | ✅ |
| `JWT_SECRET_KEY` | Secret for JWT tokens | ✅ |
| `ENCRYPTION_KEY` | Fernet encryption key | ✅ |
| `PAYSTACK_SECRET_KEY` | Paystack secret key | ✅ |
| `PAYSTACK_PUBLIC_KEY` | Paystack public key | ✅ |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | ⚠️ |
| `CLOUDINARY_API_KEY` | Cloudinary API key | ⚠️ |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | ⚠️ |
| `EMAIL_SENDER` | Email for notifications | ⚠️ |
| `EMAIL_PASSWORD` | Email app password | ⚠️ |

✅ Required | ⚠️ Optional

---

## 🎬 Demo Scenarios

### Scenario 1: Perfect Transfer Flow
```
User: "Send five thousand naira to John."
EchoBank: "Sending ₦5,000 to John Okafor at Zenith Bank. Say your PIN."
User: "1-2-3-4."
EchoBank: "PIN verified. Say confirm."
User: "Confirm."
EchoBank: "✅ Transfer successful! New balance: ₦40,320."
```

### Scenario 2: New Recipient
```
User: "Send 10,000 to Funbi."
EchoBank: "I couldn't find Funbi in your contacts. Say 'add new' to add them."
User: "Add new."
EchoBank: "What's Funbi's account number?"
[... account verification flow ...]
```

### Scenario 3: Error Recovery
```
User: "Send ₦100,000 to my brother."
EchoBank: "Your daily limit is ₦50,000. Would you like to send ₦50,000 instead?"
User: "Yes, send 20,000."
EchoBank: "Okay, sending ₦20,000 instead. Say your PIN."
```

---

## 📁 Project Structure

```
echobank/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   │   ├── voice.py      # Voice endpoints
│   │   │   ├── transfers.py  # Transfer endpoints
│   │   │   └── auth.py       # Authentication
│   │   ├── core/              # Core configuration
│   │   │   └── config.py     # Settings management
│   │   ├── models/            # Database models
│   │   │   ├── user.py
│   │   │   └── transaction.py
│   │   ├── services/          # Business logic
│   │   │   ├── whisper.py    # Speech-to-text
│   │   │   ├── llm.py        # Intent recognition
│   │   │   └── bank.py       # Bank API integration
│   │   ├── utils/             # Utilities
│   │   │   └── session.py    # Session management
│   │   └── main.py            # FastAPI app entry
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── VoiceModal/   # Voice UI modal
│   │   │   ├── Waveform/     # Audio visualizer
│   │   │   └── Transcript/   # Conversation display
│   │   ├── services/          # API services
│   │   ├── hooks/             # Custom React hooks
│   │   ├── App.jsx            # Main component
│   │   └── main.jsx           # Entry point
│   ├── package.json
│   └── vite.config.js
│
├── .env                        # Environment variables (not in git)
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

---

## 🔒 Security Features

1. **Multi-Layer Authentication**
   - Bank-issued JWT from host app
   - 4-digit Voice PIN (3 attempts max)
   - Explicit "Confirm" required for transactions

2. **Fraud Prevention**
   - Velocity checks (5 transactions/hour)
   - Daily transaction limits
   - Device binding

3. **Audit & Compliance**
   - Full conversation logging
   - Transaction timestamping
   - Voice recording retention (optional)

4. **Data Protection**
   - End-to-end encryption for sensitive data
   - No credit card/password storage
   - PCI-DSS compliant payment processing

---

## 🌐 Deployment

### Azure Web App Deployment

1. **Create Azure Web App**
   ```bash
   az webapp create --resource-group EchoBankRG --plan EchoBankPlan --name echobank-api --runtime "PYTHON:3.11"
   ```

2. **Configure Environment Variables**
   ```bash
   az webapp config appsettings set --name echobank-api --resource-group EchoBankRG --settings @appsettings.json
   ```

3. **Deploy Backend**
   ```bash
   cd backend
   zip -r deploy.zip .
   az webapp deployment source config-zip --resource-group EchoBankRG --name echobank-api --src deploy.zip
   ```

4. **Deploy Frontend** (Azure Static Web Apps)
   ```bash
   cd frontend
   npm run build
   az staticwebapp create --name echobank-frontend --resource-group EchoBankRG
   ```

### Using Supabase for Database

```env
# Update DATABASE_URL in .env
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 📊 KPIs & Metrics

| Metric | Target |
|--------|--------|
| Voice Recognition Accuracy | > 90% |
| Intent Detection | > 95% |
| Conversation Completion Rate | > 95% |
| Average Response Time | < 3s |
| Error Recovery Rate | > 80% |
| User Satisfaction | 4.5/5 |

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**TIC Hackathon Team**
- Designed for Zenith Bank integration
- Built for the underserved 52M Nigerians
- Aligned with CBN financial inclusion goals

---

## 📞 Support

For support, email [orderingpau@gmail.com](mailto:orderingpau@gmail.com) or create an issue on GitHub.

---

## 🎯 Roadmap

- [ ] Multi-language support (Yoruba, Igbo, Hausa)
- [ ] Offline mode with sync
- [ ] Biometric voice authentication
- [ ] Bill payments integration
- [ ] Savings & investment features
- [ ] USSD fallback for feature phones

---

**Made with ❤️ for inclusive banking in Nigeria**
