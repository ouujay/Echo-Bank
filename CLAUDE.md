# CLAUDE.md - Project Constitution

**This is the SOURCE OF TRUTH for EchoBank. All developers and AI assistants MUST follow these rules.**

---

## 🎯 Project Overview

**Name:** EchoBank
**Type:** Voice-Powered Banking Assistant
**Tech Stack:** FastAPI (Backend) + React + Vite (Frontend)
**Database:** PostgreSQL
**Deployment:** Azure Web Apps (Production)
**Team Size:** 3 Developers

**Purpose:** Enable visually impaired, elderly, and low-literacy users to perform banking transactions through natural voice conversations.

---

## 📁 Project Structure - NEVER DEVIATE FROM THIS

```
echobank/
├── backend/                          # Python FastAPI Backend
│   ├── app/
│   │   ├── api/                      # API Endpoints (routes)
│   │   │   ├── voice.py             # Developer 1
│   │   │   ├── recipients.py        # Developer 2
│   │   │   ├── transfers.py         # Developer 2
│   │   │   └── __init__.py
│   │   ├── core/                     # Core configuration
│   │   │   ├── config.py            # Settings (ALREADY DONE)
│   │   │   └── __init__.py
│   │   ├── models/                   # Database models
│   │   │   ├── user.py              # Developer 1
│   │   │   ├── recipient.py         # Developer 1
│   │   │   ├── transaction.py       # Developer 1
│   │   │   ├── session.py           # Developer 1
│   │   │   └── __init__.py
│   │   ├── services/                 # Business logic
│   │   │   ├── whisper.py           # Developer 1
│   │   │   ├── llm.py               # Developer 1
│   │   │   ├── auth.py              # Developer 2
│   │   │   ├── transfers.py         # Developer 2
│   │   │   ├── paystack.py          # Developer 2
│   │   │   └── __init__.py
│   │   ├── utils/                    # Utility functions
│   │   │   ├── session.py           # (ALREADY DONE)
│   │   │   └── __init__.py
│   │   └── main.py                   # FastAPI app (ALREADY DONE - just add routers)
│   ├── tests/                        # ALL DEVELOPERS
│   │   ├── test_voice.py
│   │   ├── test_transfers.py
│   │   └── test_auth.py
│   ├── alembic/                      # Database migrations
│   ├── requirements.txt              # (ALREADY DONE)
│   └── alembic.ini
│
├── frontend/                         # React + Vite Frontend
│   ├── src/
│   │   ├── components/               # React components
│   │   │   ├── VoiceModal/          # Developer 3
│   │   │   │   ├── VoiceModal.jsx
│   │   │   │   ├── VoiceModal.module.css
│   │   │   │   └── index.js
│   │   │   ├── Transcript/          # Developer 3
│   │   │   │   ├── Transcript.jsx
│   │   │   │   ├── Transcript.module.css
│   │   │   │   └── index.js
│   │   │   ├── TransferFlow/        # Developer 3
│   │   │   │   ├── PinModal.jsx
│   │   │   │   ├── ConfirmModal.jsx
│   │   │   │   └── index.js
│   │   │   └── README.md
│   │   ├── services/                 # API services
│   │   │   ├── api.js               # Developer 3
│   │   │   ├── voiceService.js      # Developer 3
│   │   │   └── transferService.js   # Developer 3
│   │   ├── hooks/                    # Custom React hooks
│   │   │   ├── useVoice.js          # Developer 3
│   │   │   ├── useTransfer.js       # Developer 3
│   │   │   └── useConversation.js   # Developer 3
│   │   ├── App.jsx                   # (ALREADY DONE - Developer 3 enhances)
│   │   ├── App.css                   # (ALREADY DONE)
│   │   ├── index.css                 # (ALREADY DONE)
│   │   └── main.jsx
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── .env                              # Environment variables (NEVER COMMIT)
├── .env.example                      # Template (ALREADY DONE)
├── .gitignore                        # (ALREADY DONE)
├── README.md                         # (ALREADY DONE)
├── TASK_DELEGATION.md               # (ALREADY DONE)
├── DEVELOPER_GUIDE.md               # (ALREADY DONE)
└── CLAUDE.md                        # THIS FILE
```

---

## 🚨 CRITICAL RULES - NEVER BREAK THESE

### 1. **NO CHANGES TO CORE CONFIGURATION**
- `backend/app/core/config.py` is **DONE**. Don't touch it.
- `backend/app/utils/session.py` is **DONE**. Don't touch it.
- `backend/app/main.py` structure is **DONE**. Only ADD routers, don't change existing code.
- `backend/requirements.txt` is **DONE**. Only add if absolutely necessary.

### 2. **ALWAYS USE THE SESSION STORE**
```python
# RIGHT WAY
from app.utils.session import session_store

session_store.set(session_id, data)
session_data = session_store.get(session_id)
```

```python
# WRONG WAY - DON'T DO THIS
# Don't use Redis or any other session storage
```

### 3. **API RESPONSE FORMAT - NEVER DEVIATE**

**Success Response:**
```json
{
  "success": true,
  "data": {
    ...actual data here...
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  }
}
```

### 4. **HTTP STATUS CODES - BE CONSISTENT**
- `200` - Success
- `400` - Bad Request (validation error, insufficient balance, limit exceeded)
- `401` - Unauthorized (wrong PIN)
- `403` - Forbidden (locked account)
- `404` - Not Found (recipient, transaction, session not found)
- `500` - Server Error (transfer failed, network error)

### 5. **DATABASE - USE THESE EXACT TABLE NAMES**
- `users` (NOT user, User, or Users)
- `recipients` (NOT beneficiaries, contacts, etc.)
- `transactions` (NOT transfers, payments, etc.)
- `sessions` (NOT user_sessions, etc.)
- `conversation_logs` (for debugging)

### 6. **NEVER HARDCODE VALUES**
```python
# RIGHT WAY
from app.core.config import settings
api_key = settings.TOGETHER_API_KEY
```

```python
# WRONG WAY - DON'T DO THIS
api_key = "984ab979a7bfd86377f59caac14125ac98bd2d788e121afc8d3ccd37165bf92c"
```

---

## 📝 Code Conventions

### Python (Backend)

**File Naming:**
- Snake case: `whisper_service.py`, `user_model.py`
- Class names: PascalCase: `WhisperService`, `UserModel`
- Function names: snake_case: `transcribe_audio()`, `verify_pin()`
- Constants: UPPER_SNAKE_CASE: `MAX_PIN_ATTEMPTS = 3`

**Import Order:**
```python
# 1. Standard library
import os
from datetime import datetime

# 2. Third-party
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

# 3. Local imports
from app.models.user import User
from app.services.auth import auth_service
from app.core.config import settings
```

**Function Documentation:**
```python
async def verify_pin(user_id: int, pin: str) -> bool:
    """
    Verify user PIN

    Args:
        user_id: User ID
        pin: Plain text PIN to verify

    Returns:
        True if PIN is correct, False otherwise

    Raises:
        HTTPException: If user is locked
    """
    pass
```

**Error Handling:**
```python
# RIGHT WAY
try:
    result = await some_service.do_something()
    return {"success": True, "data": result}
except ValueError as e:
    raise HTTPException(status_code=400, detail={
        "code": "VALIDATION_ERROR",
        "message": str(e)
    })
except Exception as e:
    raise HTTPException(status_code=500, detail={
        "code": "INTERNAL_ERROR",
        "message": "An unexpected error occurred"
    })
```

### JavaScript/React (Frontend)

**File Naming:**
- Components: PascalCase: `VoiceModal.jsx`, `PinModal.jsx`
- Services: camelCase: `voiceService.js`, `transferService.js`
- Hooks: camelCase: `useVoice.js`, `useTransfer.js`
- CSS Modules: `ComponentName.module.css`

**Component Structure:**
```javascript
import { useState, useEffect } from 'react';
import styles from './VoiceModal.module.css';

export const VoiceModal = ({ onClose, onTranscript }) => {
  // 1. State declarations
  const [isRecording, setIsRecording] = useState(false);

  // 2. useEffect hooks
  useEffect(() => {
    // cleanup
    return () => {};
  }, []);

  // 3. Event handlers
  const handleClick = () => {
    // logic
  };

  // 4. Render
  return (
    <div className={styles.modal}>
      {/* JSX */}
    </div>
  );
};
```

**API Calls:**
```javascript
// RIGHT WAY
try {
  const response = await voiceService.transcribeAudio(audioBlob);
  setTranscript(response.data.transcript);
} catch (error) {
  console.error('Transcription failed:', error);
  setError(error.response?.data?.error?.message || 'Failed to transcribe');
}
```

---

## 🔄 Git Workflow

### Branch Naming
- `feature/backend-ai` (Developer 1)
- `feature/transactions` (Developer 2)
- `feature/frontend-ui` (Developer 3)
- `bugfix/fix-pin-verification`
- `hotfix/critical-security-issue`

### Commit Messages
```
feat: Add voice transcription endpoint
fix: Correct PIN verification logic
docs: Update API documentation
test: Add tests for transfer service
refactor: Simplify session management
```

### Pull Request Process
1. **Create PR** with clear title and description
2. **Link to task** in TASK_DELEGATION.md
3. **Request review** from 1 developer
4. **Pass CI/CD** (when set up)
5. **Merge to master** after approval

### NEVER Commit These Files
- `.env` (secrets)
- `__pycache__/`
- `node_modules/`
- `*.pyc`
- `.DS_Store`
- Database dumps
- API keys in code

---

## 🎨 UI/UX Standards

### Color Palette (Defined in App.css)
```css
--primary: #0066FF         /* Main blue */
--primary-dark: #0052CC    /* Darker blue */
--primary-light: #3385FF   /* Lighter blue */
--secondary: #00D9FF       /* Cyan */
--success: #00C853         /* Green */
--bg-dark: #0A0E27         /* Dark background */
--bg-darker: #060814       /* Darker background */
--text-primary: #FFFFFF    /* White text */
--text-secondary: #A0AEC0  /* Gray text */
```

**DO NOT add new colors without team approval.**

### Component Spacing
- Padding: `8px`, `16px`, `24px`, `32px` (multiples of 8)
- Border radius: `8px`, `12px`, `16px`, `20px`
- Gaps: `8px`, `16px`, `24px`, `32px`

### Animations
- Transitions: `0.2s`, `0.3s` (fast), `0.5s` (slow)
- Easing: `ease-out`, `cubic-bezier(0.4, 0, 0.2, 1)`

---

## 🔐 Security Requirements

### Authentication Flow
1. User logs into Zenith Bank app (EXTERNAL)
2. App generates JWT token
3. Frontend sends JWT with every request
4. Backend validates JWT

```javascript
// Frontend - ALWAYS send JWT
const token = localStorage.getItem('jwt_token');
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

### PIN Handling
```python
# NEVER store plain text PINs
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"])

# Hash PIN before storing
hashed_pin = pwd_context.hash(pin)

# Verify PIN
is_valid = pwd_context.verify(plain_pin, hashed_pin)
```

### Transaction Authorization
**ALWAYS require:**
1. Valid JWT (user authenticated)
2. Correct PIN (user authorized)
3. Explicit "Confirm" command (user confirmed)

---

## 🧪 Testing Requirements

### Backend Tests (MANDATORY)

**Every endpoint MUST have a test:**
```python
# backend/tests/test_voice.py
def test_transcribe_audio():
    response = client.post("/api/v1/voice/transcribe", files={
        "audio": ("test.wav", audio_bytes, "audio/wav")
    })
    assert response.status_code == 200
    assert "transcript" in response.json()["data"]
```

### Frontend Tests (MANDATORY)

**Every component MUST have a test:**
```javascript
// VoiceModal.test.jsx
test('renders voice modal', () => {
  render(<VoiceModal onClose={() => {}} />);
  expect(screen.getByText('Voice Assistant')).toBeInTheDocument();
});
```

### Manual Testing Checklist

Before merging:
- [ ] API returns correct status codes
- [ ] Error messages are user-friendly
- [ ] Voice recording works in Chrome & Firefox
- [ ] Mobile responsive (test on phone)
- [ ] All console errors resolved

---

## 🚫 Common Mistakes to AVOID

### Backend

❌ **DON'T:** Use `print()` for debugging
✅ **DO:** Use `logging` module

❌ **DON'T:** Return raw SQLAlchemy models
✅ **DO:** Convert to Pydantic models or dictionaries

❌ **DON'T:** Use `except Exception: pass`
✅ **DO:** Handle specific exceptions and log errors

❌ **DON'T:** Store PINs in plain text
✅ **DO:** Use bcrypt to hash PINs

❌ **DON'T:** Hard-code API keys
✅ **DO:** Use `settings.API_KEY`

### Frontend

❌ **DON'T:** Use inline styles
✅ **DO:** Use CSS modules

❌ **DON'T:** Store JWT in state
✅ **DO:** Store in localStorage

❌ **DON'T:** Fetch data in render
✅ **DO:** Use useEffect

❌ **DON'T:** Ignore error states
✅ **DO:** Show user-friendly error messages

❌ **DON'T:** Use `var`
✅ **DO:** Use `const` or `let`

---

## 📊 Database Guidelines

### Model Relationships
```python
# User has many Recipients
class User(Base):
    recipients = relationship("Recipient", back_populates="user")

# Recipient belongs to User
class Recipient(Base):
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="recipients")
```

### Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Add users table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Queries
```python
# EFFICIENT - Use filters
users = db.query(User).filter(User.is_active == True).all()

# INEFFICIENT - Don't do this
all_users = db.query(User).all()
active_users = [u for u in all_users if u.is_active]
```

---

## 🤖 Working with Claude (AI Assistant)

### When Asking Claude for Help

**DO:**
✅ "Following CLAUDE.md, implement voice transcription in backend/app/services/whisper.py"
✅ "Using the API contract in DEVELOPER_GUIDE.md, create the /api/v1/recipients/search endpoint"
✅ "Add error handling to the PIN verification according to the patterns in CLAUDE.md"

**DON'T:**
❌ "Create a voice service" (too vague)
❌ "Write some code for transfers" (no context)
❌ "Make it work" (not specific)

### Claude's Rules When Helping

**Claude MUST:**
1. Read `CLAUDE.md`, `DEVELOPER_GUIDE.md`, and `TASK_DELEGATION.md` FIRST
2. Follow the exact API response format
3. Use the exact file structure
4. Follow code conventions
5. Include error handling
6. Add documentation
7. NOT change core files (config.py, session.py, main.py structure)

**Claude MUST NOT:**
1. Change the project structure
2. Add new dependencies without asking
3. Change API contracts without team agreement
4. Introduce new design patterns
5. Skip error handling
6. Ignore testing requirements

---

## 📞 Communication Protocol

### Daily Standup (10 minutes)
**Format:**
```
Developer 1 (Backend AI):
- Completed: Whisper service
- Today: LLM intent parsing
- Blockers: Need Bedrock API key

Developer 2 (Transactions):
- Completed: Auth service
- Today: Transfer initiation endpoint
- Blockers: None

Developer 3 (Frontend):
- Completed: Voice modal UI
- Today: API integration
- Blockers: Waiting for backend endpoints
```

### Slack Channels
- `#echobank-dev` - General discussions
- `#echobank-backend` - Backend questions
- `#echobank-frontend` - Frontend questions
- `#echobank-blockers` - URGENT issues

### Code Review Etiquette
- Be respectful and constructive
- Explain WHY something should change
- Approve if code follows CLAUDE.md
- Request changes if it violates guidelines

---

## 🎯 Definition of Done

A task is **DONE** when:
- [ ] Code follows conventions in CLAUDE.md
- [ ] API contract matches DEVELOPER_GUIDE.md
- [ ] Tests are written and passing
- [ ] Error handling is implemented
- [ ] Documentation is updated
- [ ] Code is reviewed and approved
- [ ] Branch is merged to master
- [ ] Works in development environment
- [ ] No console errors

---

## 📚 Documentation Hierarchy

1. **CLAUDE.md** (THIS FILE) - Source of truth for conventions and rules
2. **DEVELOPER_GUIDE.md** - Technical implementation details and code examples
3. **TASK_DELEGATION.md** - Who does what and when
4. **README.md** - Project overview and setup instructions
5. **API Docs** - http://localhost:8000/docs (auto-generated)

**If there's a conflict, CLAUDE.md wins.**

---

## 🚀 Deployment Checklist

Before deploying to Azure:
- [ ] All tests pass
- [ ] Environment variables set in Azure
- [ ] Database migrations applied
- [ ] CORS origins include production URL
- [ ] API keys are in Azure Key Vault (not .env)
- [ ] Frontend points to production API
- [ ] Error tracking enabled (Sentry)
- [ ] Performance monitoring enabled
- [ ] Backup strategy in place

---

## ⚡ Quick Reference

### Start Development
```bash
# Backend
cd backend
source ../venv/bin/activate  # or .\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm run dev
```

### Environment Variables
```bash
# Copy template
cp .env.example .env

# Edit with your keys
nano .env  # or use your editor
```

### Database
```bash
# Create database
psql -U postgres -c "CREATE DATABASE echobank;"

# Run migrations
alembic upgrade head
```

### Testing
```bash
# Backend
pytest backend/tests/

# Frontend
npm test
```

---

## 🆘 Emergency Contacts

**Project Lead:** [Your Name]
**Tech Lead:** [Tech Lead Name]
**Slack:** #echobank-emergency
**GitHub Issues:** https://github.com/ouujay/Echo-Bank/issues

---

## ✅ Version Control

**CLAUDE.md Version:** 1.0
**Last Updated:** 2025-10-24
**Next Review:** Before Week 2 integration

**Changes require team approval.**

---

## 🎓 Onboarding Checklist

New developer joining? Complete this:
- [ ] Read CLAUDE.md (this file)
- [ ] Read README.md
- [ ] Read TASK_DELEGATION.md
- [ ] Read DEVELOPER_GUIDE.md
- [ ] Clone repository
- [ ] Set up .env file
- [ ] Run backend and frontend
- [ ] Create your feature branch
- [ ] Make first commit
- [ ] Attend daily standup

---

**This is the law. Follow it, and we ship on time. Break it, and we chaos. 🚀**

**Questions? Ask in #echobank-dev before breaking the rules.**
