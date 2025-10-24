# EchoBank - Team Task Delegation

## Team Structure (3 Developers)

This document splits the work across **3 developers** working in parallel. Each developer has a clearly defined area of responsibility with minimal overlap to maximize efficiency.

---

## 👤 Developer 1: Backend Core & AI Integration

**Primary Focus:** FastAPI backend, AI services, and database

### Tasks:

#### 1. Voice Processing Service (`backend/app/services/whisper.py`)
- [ ] Integrate OpenAI Whisper API for speech-to-text
- [ ] Handle audio file uploads (multipart/form-data)
- [ ] Add error handling for unclear voice
- [ ] Implement retry logic (max 3 attempts)
- [ ] Return transcribed text with confidence score

#### 2. LLM Intent Recognition (`backend/app/services/llm.py`)
- [ ] Integrate Together AI / OpenAI for intent parsing
- [ ] Create prompt engineering for transaction intents
- [ ] Extract entities: recipient, amount, action type
- [ ] Handle ambiguous commands
- [ ] Return structured JSON intent

#### 3. Database Models (`backend/app/models/`)
- [ ] Create User model (id, name, account_number, pin_hash)
- [ ] Create Recipient model (user_id, name, account_number, bank)
- [ ] Create Transaction model (sender, receiver, amount, status, timestamp)
- [ ] Create Session model (session_id, user_id, context, expires_at)
- [ ] Set up Alembic migrations

#### 4. Voice API Endpoints (`backend/app/api/voice.py`)
- [ ] POST `/api/v1/voice/transcribe` - Upload audio, return text
- [ ] POST `/api/v1/voice/intent` - Parse intent from text
- [ ] GET `/api/v1/voice/session/{session_id}` - Get session state
- [ ] POST `/api/v1/voice/session/{session_id}/update` - Update context

#### 5. Testing & Documentation
- [ ] Write unit tests for voice service
- [ ] Write unit tests for LLM service
- [ ] Add API documentation (FastAPI auto-docs)
- [ ] Test error scenarios

**API Keys Needed:**
- `TOGETHER_API_KEY` or OpenAI key
- `WHISPERAPI` (OpenAI)
- `DATABASE_URL` (create echobank database)

**Branch:** `feature/backend-ai`

---

## 👤 Developer 2: Transaction Logic & Bank Integration

**Primary Focus:** Transfer flows, Paystack integration, authentication

### Tasks:

#### 1. Authentication Service (`backend/app/services/auth.py`)
- [ ] JWT token validation (from bank app)
- [ ] Voice PIN verification (bcrypt hash comparison)
- [ ] PIN attempt tracking (max 3, lockout 30 min)
- [ ] Session management
- [ ] Device binding validation

#### 2. Recipient Management (`backend/app/api/recipients.py`)
- [ ] GET `/api/v1/recipients` - List saved recipients
- [ ] POST `/api/v1/recipients/search?name=John` - Search by name
- [ ] POST `/api/v1/recipients` - Add new recipient
- [ ] POST `/api/v1/recipients/verify` - Verify account number
- [ ] Handle multiple matches (disambiguation)

#### 3. Transfer Service (`backend/app/services/transfers.py`)
- [ ] State machine for transfer flow
  - Collect recipient
  - Verify amount & balance
  - Request PIN
  - Confirm
  - Execute
- [ ] Balance check integration
- [ ] Daily/hourly limit enforcement
- [ ] Transfer execution (Paystack or bank API)
- [ ] SMS notification trigger

#### 4. Transfer API Endpoints (`backend/app/api/transfers.py`)
- [ ] POST `/api/v1/transfers/initiate` - Start transfer
- [ ] POST `/api/v1/transfers/{transfer_id}/verify-pin` - Verify PIN
- [ ] POST `/api/v1/transfers/{transfer_id}/confirm` - Confirm transfer
- [ ] POST `/api/v1/transfers/{transfer_id}/cancel` - Cancel transfer
- [ ] GET `/api/v1/transfers/{transfer_id}` - Get transfer status

#### 5. Paystack Integration (`backend/app/services/paystack.py`)
- [ ] Initialize transfer to recipient account
- [ ] Verify account number/name
- [ ] Handle webhooks for transfer status
- [ ] Implement retry logic for failed transfers
- [ ] Log all transactions for audit

**API Keys Needed:**
- `PAYSTACK_SECRET_KEY`
- `PAYSTACK_PUBLIC_KEY`
- `JWT_SECRET_KEY`
- `ENCRYPTION_KEY`

**Branch:** `feature/transactions`

---

## 👤 Developer 3: Frontend & User Experience

**Primary Focus:** React UI, voice interaction, conversation flow

### Tasks:

#### 1. Voice Interaction Component (`frontend/src/components/VoiceModal/`)
- [ ] Create VoiceModal.jsx - Main voice UI
- [ ] Implement Web Speech API for browser recording
- [ ] Add visual waveform animation during recording
- [ ] Display "Listening..." / "Processing..." states
- [ ] Handle start/stop recording
- [ ] Send audio to backend `/api/v1/voice/transcribe`

#### 2. Conversation Display (`frontend/src/components/Transcript/`)
- [ ] Create Transcript.jsx component
- [ ] Display user messages (right-aligned, blue)
- [ ] Display bot messages (left-aligned, gray)
- [ ] Auto-scroll to latest message
- [ ] Clear conversation button
- [ ] Timestamp display

#### 3. Transfer Flow UI (`frontend/src/components/TransferFlow/`)
- [ ] Create PIN input modal (4 digits)
- [ ] Create confirmation modal
- [ ] Create success/failure screens
- [ ] Handle recipient disambiguation (multiple Johns)
- [ ] Display balance after transaction
- [ ] Show transaction receipt

#### 4. API Service Layer (`frontend/src/services/`)
- [ ] Create `api.js` - Axios instance with base URL
- [ ] Create `voiceService.js` - Voice API calls
- [ ] Create `transferService.js` - Transfer API calls
- [ ] Create `authService.js` - JWT handling
- [ ] Add error handling & retry logic

#### 5. State Management (`frontend/src/hooks/`)
- [ ] Create `useVoice.js` - Voice recording hook
- [ ] Create `useTransfer.js` - Transfer state hook
- [ ] Create `useConversation.js` - Message management
- [ ] Add loading states
- [ ] Add error states

#### 6. Premium UI Enhancements
- [ ] Add smooth transitions & animations
- [ ] Implement dark mode toggle
- [ ] Add accessibility features (ARIA labels)
- [ ] Add keyboard shortcuts (Space to record)
- [ ] Mobile responsive design
- [ ] Add TTS (Text-to-Speech) for bot responses

#### 7. Testing
- [ ] Write unit tests for components
- [ ] Write integration tests for API calls
- [ ] Test voice recording in different browsers
- [ ] Test mobile responsiveness

**Environment Variables:**
- `VITE_API_URL=http://localhost:8000`

**Branch:** `feature/frontend-ui`

---

## 🔄 Integration Checkpoints

### Week 1 Sync (After 3 Days)
**Goal:** Merge all branches and test end-to-end flow

**Developer 1 delivers:**
- Working voice transcription endpoint
- Working intent recognition endpoint
- Database models migrated

**Developer 2 delivers:**
- Working transfer initiation endpoint
- PIN verification endpoint
- Paystack test integration

**Developer 3 delivers:**
- Working voice recording UI
- API service layer complete
- Basic conversation display

**Test Together:**
1. Record voice → Transcribe → Parse intent
2. Initiate transfer → Verify PIN → Execute
3. Display full conversation flow

### Week 2 Sync (Final Integration)
**Goal:** Polish, edge cases, and deployment

**All developers:**
- Fix integration bugs
- Handle edge cases (13 scenarios from PRD)
- Write tests
- Deploy to Azure

---

## 📋 Shared Resources

### API Contracts (Must Agree On)

#### Voice Transcription Response
```json
{
  "transcript": "Send 5000 naira to John",
  "confidence": 0.95,
  "session_id": "SESSION123"
}
```

#### Intent Recognition Response
```json
{
  "intent": "transfer",
  "entities": {
    "recipient": "John",
    "amount": 5000,
    "currency": "NGN"
  },
  "confidence": 0.92
}
```

#### Transfer Initiation Response
```json
{
  "transfer_id": "TXN123",
  "status": "pending_pin",
  "recipient": {
    "name": "John Okafor",
    "account": "0123456789",
    "bank": "Zenith Bank"
  },
  "amount": 5000,
  "message": "Please say your 4-digit PIN"
}
```

---

## 🚀 Getting Started

### For Each Developer:

1. **Clone & Create Branch**
   ```bash
   git checkout -b [your-branch-name]
   ```

2. **Set Up Environment**
   - Copy `.env.example` to `.env`
   - Add your assigned API keys
   - Create database (Developer 1 only)

3. **Install Dependencies**
   ```bash
   # Backend (Developers 1 & 2)
   cd backend
   pip install -r requirements.txt

   # Frontend (Developer 3)
   cd frontend
   npm install
   ```

4. **Run Servers**
   ```bash
   # Backend
   cd backend
   uvicorn app.main:app --reload --port 8000

   # Frontend
   cd frontend
   npm run dev
   ```

5. **Daily Sync**
   - Push your changes daily
   - Pull from `master` to stay updated
   - Communicate blockers in team chat

---

## 📞 Communication Protocol

**Daily Standup (10 min):**
- What did I complete yesterday?
- What am I working on today?
- Any blockers?

**Slack Channels:**
- `#echobank-dev` - General development
- `#echobank-backend` - Backend discussions
- `#echobank-frontend` - Frontend discussions
- `#echobank-integration` - Integration issues

**Code Review:**
- All PRs need 1 approval before merge
- Test your code before creating PR
- Add screenshots for UI changes

---

## ✅ Definition of Done

A task is complete when:
- [ ] Code is written and tested
- [ ] Unit tests pass
- [ ] Integrated with other components
- [ ] Documentation updated
- [ ] PR approved and merged

---

**Good luck! Let's build something amazing! 🚀**
