# EchoBank Frontend

**Voice-Powered Banking Interface**

The EchoBank frontend is a React-based web application that provides a voice-first banking experience for visually impaired, elderly, and low-literacy users.

---

## 🎯 Purpose

EchoBank enables users to perform banking operations using their voice:
- Check account balance
- Send money to recipients
- Manage recipients/beneficiaries
- View transaction history
- All through natural voice commands

---

## 🏗️ Architecture

### Tech Stack
- **React 19** - UI framework
- **Vite** - Build tool and dev server
- **Axios** - HTTP client for API calls
- **CSS Modules** - Component-scoped styling

### Project Structure

```
frontend/src/
├── components/          # React components
│   ├── VoiceModal/     # Voice recording interface
│   ├── Transcript/     # Display voice transcripts
│   ├── TransferFlow/   # PIN and confirmation modals
│   └── DemoToggle/     # Demo mode toggle
├── services/           # API integration layer
│   ├── api.js         # Axios instance with auth
│   ├── voiceService.js # Voice/transcription API
│   ├── transferService.js # Transfer/recipient API
│   └── mockService.js  # Mock data for demo mode
├── hooks/             # Custom React hooks
│   ├── useVoice.js    # Voice recording logic
│   └── useTransfer.js # Transfer flow logic
├── App.jsx            # Main application component
├── App.css            # Global styles (EchoBank design system)
└── main.jsx           # Application entry point
```

---

## 🎨 Design System

### Color Palette

```css
/* Primary Colors */
--primary: #0066FF         /* Main blue */
--primary-dark: #0052CC    /* Darker blue */
--primary-light: #3385FF   /* Lighter blue */

/* Status Colors */
--success: #00C853         /* Green - successful transfers */
--danger: #FF3B30          /* Red - errors, debits */
--warning: #FFB800         /* Yellow - warnings */

/* Neutral Colors */
--white: #FFFFFF
--gray-50 to --gray-900    /* Gray scale */

/* Spacing */
8px, 16px, 24px, 32px      /* Multiples of 8 */

/* Border Radius */
8px, 12px, 16px, 20px      /* Consistent rounding */
```

### Design Principles

1. **Voice-First**: Voice button is prominent (floating action button)
2. **High Contrast**: Easy to read for visually impaired users
3. **Large Touch Targets**: Minimum 44px × 44px for accessibility
4. **Clear Feedback**: Visual and audio confirmation of actions
5. **Minimal Text Entry**: Everything can be done by voice

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Configuration

Create or update `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

### Development

```bash
npm run dev
```

Opens at `http://localhost:5173`

### Production Build

```bash
npm run build
npm run preview
```

---

## 🎤 Key Features

### 1. Voice Recording

**Component**: `VoiceModal`

- Records user voice input
- Auto-stops after 5 seconds
- Sends audio to backend for transcription
- Displays transcript for confirmation

**Usage**:
```javascript
import { VoiceModal } from './components/VoiceModal/VoiceModal';

<VoiceModal
  onClose={() => setShowModal(false)}
  onTranscript={(text, intent) => handleVoiceCommand(text, intent)}
/>
```

### 2. Balance Display

**Component**: Integrated in `App.jsx`

- Shows current account balance
- Auto-refreshes after transactions
- Large, readable font (2.5rem)
- Nigerian Naira (₦) formatting

### 3. Quick Actions

**Component**: Quick action buttons in `App.jsx`

Pre-configured voice commands:
- "What's my balance?"
- "Send 1000 naira to John Doe"
- "Show my recipients"
- "Show my transactions"

### 4. Transfer Flow

**Components**: `PinModal`, `ConfirmModal`

Multi-step transfer process:
1. Voice: "Send 5000 to John"
2. Backend finds recipient
3. Request PIN (voice or keyboard)
4. Confirm transfer details
5. Execute and show confirmation

### 5. Conversation History

**Component**: Voice overlay in `App.jsx`

- Shows full conversation with bot
- User messages (right-aligned, blue)
- Bot responses (left-aligned, gray)
- Intent badges for debugging
- Audio playback of TTS responses

---

## 🔌 API Integration

### Services

**1. Voice Service** (`services/voiceService.js`)

```javascript
import { voiceService } from './services/voiceService';

// Transcribe audio
const result = await voiceService.transcribeAudio(audioBlob, sessionId);
// Returns: { transcript, confidence, session_id }

// Parse intent
const intent = await voiceService.parseIntent(transcript, sessionId);
// Returns: { intent, entities, next_step }

// Get session
const session = await voiceService.getSession(sessionId);
```

**2. Transfer Service** (`services/transferService.js`)

```javascript
import { transferService } from './services/transferService';

// Search recipients
const recipients = await transferService.searchRecipients("John");

// Initiate transfer
const transfer = await transferService.initiateTransfer(recipientId, amount, sessionId);

// Verify PIN
await transferService.verifyPin(transferId, pin);

// Confirm transfer
await transferService.confirmTransfer(transferId);

// Cancel transfer
await transferService.cancelTransfer(transferId);
```

### Error Handling

All API calls handle errors consistently:

```javascript
try {
  const response = await voiceService.transcribeAudio(audioBlob);
  // Handle success
} catch (error) {
  // error.response.data contains structured error:
  // {
  //   success: false,
  //   error: {
  //     code: "VOICE_UNCLEAR",
  //     message: "Voice not clear. Please speak again."
  //   }
  // }
}
```

---

## 🧪 Testing

### Manual Testing Checklist

**Voice Recording**:
- [ ] Click voice button opens modal
- [ ] Microphone permission requested
- [ ] Recording indicator appears
- [ ] Audio stops after 5 seconds
- [ ] Transcript displays correctly
- [ ] "Continue" button works

**Balance Check**:
- [ ] Balance displays correctly
- [ ] Format: ₦45,320.00
- [ ] Refreshes after transfer

**Transfer Flow**:
- [ ] Voice command initiates transfer
- [ ] Recipient search works
- [ ] Multiple recipients show options
- [ ] PIN modal appears
- [ ] Correct PIN proceeds
- [ ] Wrong PIN shows error with attempts remaining
- [ ] Confirmation modal shows details
- [ ] Transfer executes successfully
- [ ] New balance updates

**Audio Feedback**:
- [ ] TTS responses play automatically
- [ ] Audio element hidden
- [ ] Playback controls work

---

## 🎯 Voice Command Examples

### Balance Check
- "What's my balance?"
- "Check my balance"
- "How much money do I have?"

### Send Money
- "Send 5000 naira to John"
- "Transfer 10000 to Mary"
- "Pay 2000 to John Okafor"

### Recipients
- "Show my recipients"
- "List my contacts"
- "Who can I send money to?"

### Transactions
- "Show my transactions"
- "What are my recent transactions?"
- "Transaction history"

### PIN Entry
- "1 2 3 4"
- "One two three four"
- (Keyboard entry also supported)

### Confirmation
- "Confirm"
- "Yes, send it"
- "Cancel" (to abort)

---

## 🔒 Security

### JWT Authentication

All API requests include JWT token:

```javascript
// Stored in localStorage
const token = localStorage.getItem('jwt_token');

// Automatically added by axios interceptor
api.interceptors.request.use((config) => {
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### PIN Protection

- PINs never stored in frontend
- Sent to backend for verification
- 3 attempts before 30-minute lockout
- PIN entry via voice or keyboard

### Session Management

- Session IDs generated per conversation
- 30-minute expiry
- State stored server-side (not in frontend)

---

## 📱 Responsive Design

### Breakpoints

```css
/* Desktop: Default styles */
@media (max-width: 768px) {
  /* Tablet */
  .quick-actions { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 480px) {
  /* Mobile */
  .balance-amount { font-size: 2rem; }
  .voice-fab { width: 56px; height: 56px; }
}
```

### Mobile Optimizations

- Voice button: 56px × 56px (from 64px on desktop)
- Quick actions: 2 columns (from 4 on desktop)
- Larger touch targets (minimum 44px)
- Simplified transaction cards

---

## 🐛 Common Issues

### Voice Recording Not Working

**Problem**: "Microphone access denied"

**Solution**:
1. Check browser permissions (chrome://settings/content/microphone)
2. Use HTTPS or localhost (HTTP blocked on other domains)
3. Try different browser (Chrome/Edge recommended)

### API Connection Failed

**Problem**: "Network Error" or "ERR_CONNECTION_REFUSED"

**Solution**:
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify .env has correct API URL
3. Check CORS settings in backend config.py

### TTS Audio Not Playing

**Problem**: Voice responses not audible

**Solution**:
1. Check browser console for errors
2. Verify audio element exists in DOM
3. Check browser audio permissions
4. Ensure backend includes_audio: true in response

---

## 📚 Component Documentation

### VoiceModal

**Purpose**: Captures user voice input

**Props**:
- `onClose: () => void` - Called when modal closes
- `onTranscript: (text: string, intent: object) => void` - Called with transcript and parsed intent

**State**:
- `isRecording: boolean` - Currently recording
- `isProcessing: boolean` - Transcribing audio
- `transcript: string` - Transcribed text

### useVoice Hook

**Purpose**: Handles voice recording logic

**Returns**:
```javascript
{
  isRecording: boolean,
  isProcessing: boolean,
  transcript: string,
  error: string | null,
  startRecording: () => Promise<void>,
  stopRecording: () => void
}
```

**Usage**:
```javascript
const { isRecording, startRecording, stopRecording } = useVoice();

// Start recording
await startRecording();

// Stop after 5 seconds
setTimeout(stopRecording, 5000);
```

---

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

Generates optimized files in `dist/` folder.

### Environment Variables

**Production `.env`**:
```env
VITE_API_URL=https://echobank-api.azurewebsites.net
```

### Azure Deployment

1. Build production bundle
2. Upload `dist/` contents to Azure Static Web Apps
3. Configure API URL environment variable
4. Enable HTTPS and custom domain

---

## 📊 Performance

### Optimization Strategies

1. **Code Splitting**: Components lazy-loaded
2. **Image Optimization**: Icons use emojis (no image files)
3. **CSS Modules**: Scoped styles prevent conflicts
4. **Audio Caching**: TTS responses cached in audio element
5. **API Debouncing**: Voice commands debounced to prevent spam

### Target Metrics

- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3s
- **Lighthouse Score**: > 90

---

## 🤝 Contributing

### Code Style

Follow CLAUDE.md conventions:
- Use functional components (not class components)
- Use CSS Modules for styling (not inline styles)
- Use const/let (not var)
- Handle errors with try/catch
- Add PropTypes for components

### Pull Request Process

1. Create feature branch: `feature/frontend-[feature-name]`
2. Implement changes following CLAUDE.md
3. Test manually (voice, transfers, balance)
4. Create PR with description
5. Request review from Developer 3 or team lead
6. Merge after approval

---

## 📝 License

Proprietary - EchoBank Project

---

## 📞 Support

- **Slack**: #echobank-frontend
- **Email**: dev@echobank.com
- **GitHub Issues**: https://github.com/ouujay/Echo-Bank/issues

---

**Built with ❤️ for accessibility and financial inclusion**
