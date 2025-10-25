# EchoBank Frontend Components

**Component Documentation and Usage Guide**

This document provides detailed information about all React components in the EchoBank frontend.

---

## 📦 Component Overview

### Component Structure

```
components/
├── VoiceModal/           # Voice recording interface
│   ├── VoiceModal.jsx
│   ├── VoiceModal.module.css
│   └── index.js
├── Transcript/           # Transcript display
│   ├── Transcript.jsx
│   ├── Transcript.module.css
│   └── index.js
├── TransferFlow/         # Transfer modals
│   ├── PinModal.jsx
│   ├── ConfirmModal.jsx
│   └── index.js
└── DemoToggle/          # Demo mode toggle
    ├── DemoToggle.jsx
    ├── DemoToggle.module.css
    └── index.js
```

---

## 🎤 VoiceModal

**Purpose**: Provides voice recording interface for user input

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `onClose` | `() => void` | Yes | Callback when modal is closed |
| `onTranscript` | `(text: string, intent: object) => void` | Yes | Callback with transcription result |

### Usage Example

```jsx
import { VoiceModal } from './components/VoiceModal/VoiceModal';

function App() {
  const [showModal, setShowModal] = useState(false);

  const handleTranscript = (text, intent) => {
    console.log('User said:', text);
    console.log('Intent:', intent);
    setShowModal(false);
  };

  return (
    <>
      <button onClick={() => setShowModal(true)}>🎤 Speak</button>

      {showModal && (
        <VoiceModal
          onClose={() => setShowModal(false)}
          onTranscript={handleTranscript}
        />
      )}
    </>
  );
}
```

### Features

- **Auto-start recording**: Begins recording when modal opens
- **5-second limit**: Automatically stops after 5 seconds
- **Visual feedback**: Pulse animation while recording
- **Transcript display**: Shows transcribed text before proceeding
- **Intent parsing**: Calls LLM service to understand user command

### States

- **Starting**: Modal opened, initializing microphone
- **Recording**: Actively capturing audio (pulse animation)
- **Processing**: Sending audio to backend for transcription
- **Transcribed**: Showing transcript with "Continue" button

### Error Handling

```jsx
try {
  await startRecording();
} catch (error) {
  // Shows error message if microphone access denied
  console.error('Microphone access denied');
}
```

### Styling

Uses CSS Modules for scoped styles:
- `overlay`: Full-screen backdrop (rgba(0, 0, 0, 0.7))
- `modal`: Centered modal with gradient background
- `voiceButton`: Circular button with pulse animation
- `transcript`: Transcript display area

---

## 📝 Transcript

**Purpose**: Displays conversation history between user and bot

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `messages` | `Array<Message>` | Yes | Array of conversation messages |
| `isLoading` | `boolean` | No | Shows typing indicator |

### Message Type

```typescript
type Message = {
  type: 'user' | 'bot',
  text: string,
  intent?: string,
  timestamp: Date,
  audio?: string  // Base64 audio data
}
```

### Usage Example

```jsx
import { Transcript } from './components/Transcript/Transcript';

function App() {
  const [conversation, setConversation] = useState([
    { type: 'user', text: 'What\'s my balance?', timestamp: new Date() },
    { type: 'bot', text: 'Your balance is ₦45,320.00', intent: 'check_balance', timestamp: new Date() }
  ]);

  return (
    <Transcript
      messages={conversation}
      isLoading={false}
    />
  );
}
```

### Features

- **Message bubbles**: Different colors for user (blue) vs bot (gray)
- **Avatars**: User icon (👤) vs Bot icon (🤖)
- **Intent badges**: Shows detected intent for debugging
- **Typing indicator**: Animated dots when bot is processing
- **Auto-scroll**: Scrolls to bottom on new messages

### Styling

- User messages: Right-aligned, blue background (`--primary`)
- Bot messages: Left-aligned, gray background (`--gray-100`)
- Intent badges: Small blue pill with intent name

---

## 💳 TransferFlow Components

### PinModal

**Purpose**: Captures user's 4-digit PIN for transfer authorization

#### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `onSubmit` | `(pin: string) => void` | Yes | Callback with entered PIN |
| `onCancel` | `() => void` | Yes | Callback when user cancels |
| `attemptsRemaining` | `number` | No | Show remaining attempts |
| `isLoading` | `boolean` | No | Show loading state |

#### Usage Example

```jsx
import { PinModal } from './components/TransferFlow/PinModal';

function TransferPage() {
  const [showPin, setShowPin] = useState(false);

  const handlePinSubmit = async (pin) => {
    try {
      await transferService.verifyPin(transferId, pin);
      setShowPin(false);
    } catch (error) {
      console.error('Invalid PIN');
    }
  };

  return (
    <>
      {showPin && (
        <PinModal
          onSubmit={handlePinSubmit}
          onCancel={() => setShowPin(false)}
          attemptsRemaining={3}
          isLoading={false}
        />
      )}
    </>
  );
}
```

#### Features

- **4-digit input**: Automatically advances between digits
- **Voice support**: Can also accept PIN via voice
- **Masking**: Shows bullets (••••) instead of numbers
- **Attempts counter**: Shows remaining attempts (3/2/1)
- **Auto-focus**: Focuses first digit on mount
- **Keyboard navigation**: Arrow keys, backspace, paste support

---

### ConfirmModal

**Purpose**: Shows transfer details and requests final confirmation

#### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `transfer` | `Transfer` | Yes | Transfer details object |
| `onConfirm` | `() => void` | Yes | Callback when confirmed |
| `onCancel` | `() => void` | Yes | Callback when cancelled |

#### Transfer Type

```typescript
type Transfer = {
  recipient: {
    name: string,
    account_number: string,
    bank_name: string
  },
  amount: number,
  current_balance: number,
  new_balance: number
}
```

#### Usage Example

```jsx
import { ConfirmModal } from './components/TransferFlow/ConfirmModal';

function TransferPage() {
  const [transfer, setTransfer] = useState(null);

  const handleConfirm = async () => {
    try {
      await transferService.confirmTransfer(transfer.id);
      alert('Transfer successful!');
    } catch (error) {
      console.error('Transfer failed');
    }
  };

  return (
    <>
      {transfer && (
        <ConfirmModal
          transfer={transfer}
          onConfirm={handleConfirm}
          onCancel={() => setTransfer(null)}
        />
      )}
    </>
  );
}
```

#### Features

- **Transfer summary**: Shows recipient, amount, balances
- **Balance preview**: Current balance → New balance
- **Large text**: Easy to read (18px+)
- **Confirm/Cancel buttons**: Clear action buttons
- **Voice confirmation**: Can also say "Confirm" or "Cancel"

---

## 🔄 DemoToggle

**Purpose**: Switches between demo mode and live mode

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `isDemoMode` | `boolean` | Yes | Current mode state |
| `onToggle` | `() => void` | Yes | Callback when toggled |

### Usage Example

```jsx
import { DemoToggle } from './components/DemoToggle/DemoToggle';

function App() {
  const [demoMode, setDemoMode] = useState(false);

  return (
    <DemoToggle
      isDemoMode={demoMode}
      onToggle={() => setDemoMode(!demoMode)}
    />
  );
}
```

### Features

- **Toggle switch**: On/off switch design
- **Labels**: "Demo" and "Live" text
- **Color indicator**: Blue when active, gray when inactive
- **Smooth transition**: Animated slide effect

---

## 🎨 Styling Guidelines

### CSS Modules

All components use CSS Modules to prevent style conflicts:

```jsx
// Component file
import styles from './VoiceModal.module.css';

<div className={styles.modal}>
  <button className={styles.closeBtn}>×</button>
</div>
```

```css
/* VoiceModal.module.css */
.modal {
  background: white;
  border-radius: 20px;
}

.closeBtn {
  background: transparent;
  border: none;
}
```

### Design Tokens

Use CSS variables from `App.css`:

```css
.modal {
  background: var(--white);
  color: var(--gray-900);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-xl);
}
```

### Common Patterns

**Modal Overlay**:
```css
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
```

**Button Styles**:
```css
.primaryButton {
  background: var(--primary);
  color: var(--white);
  border: none;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.primaryButton:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
}
```

---

## ♿ Accessibility

### Requirements

All components must meet:
- **WCAG 2.1 Level AA** compliance
- **Keyboard navigation** support
- **Screen reader** compatibility
- **Color contrast** ratios (minimum 4.5:1)

### Implementation

**Keyboard Support**:
```jsx
// PinModal.jsx
<input
  type="text"
  maxLength="1"
  onKeyDown={(e) => {
    if (e.key === 'ArrowRight') focusNext();
    if (e.key === 'ArrowLeft') focusPrev();
    if (e.key === 'Backspace') clearAndFocusPrev();
  }}
/>
```

**ARIA Labels**:
```jsx
<button
  aria-label="Start voice recording"
  onClick={startRecording}
>
  🎤
</button>
```

**Focus Management**:
```jsx
useEffect(() => {
  // Auto-focus first input when modal opens
  inputRef.current?.focus();
}, []);
```

---

## 🧪 Testing

### Unit Testing

**Example test for VoiceModal**:

```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import { VoiceModal } from './VoiceModal';

test('renders voice modal with recording button', () => {
  render(<VoiceModal onClose={() => {}} onTranscript={() => {}} />);

  expect(screen.getByText('Voice Assistant')).toBeInTheDocument();
  expect(screen.getByRole('button')).toBeInTheDocument();
});

test('calls onClose when close button clicked', () => {
  const onClose = jest.fn();
  render(<VoiceModal onClose={onClose} onTranscript={() => {}} />);

  fireEvent.click(screen.getByText('×'));
  expect(onClose).toHaveBeenCalled();
});
```

### Integration Testing

Test full user flows:

1. **Voice Recording Flow**:
   - Click voice button → Modal opens
   - Recording starts → Pulse animation
   - Stop after 5s → Shows transcript
   - Click continue → Calls onTranscript

2. **Transfer Flow**:
   - Initiate transfer → PIN modal opens
   - Enter PIN → Confirm modal opens
   - Click confirm → Transfer executes

---

## 🚀 Performance

### Optimization Tips

1. **Lazy Loading**:
```jsx
const VoiceModal = lazy(() => import('./components/VoiceModal/VoiceModal'));

<Suspense fallback={<div>Loading...</div>}>
  {showModal && <VoiceModal />}
</Suspense>
```

2. **Memoization**:
```jsx
const MemoizedTranscript = memo(Transcript, (prev, next) => {
  return prev.messages.length === next.messages.length;
});
```

3. **CSS Optimization**:
- Use CSS Modules (scoped styles)
- Avoid inline styles
- Use CSS animations (not JavaScript)

---

## 📚 Additional Resources

- **Design System**: See `App.css` for color palette and spacing
- **API Integration**: See `services/` folder for API calls
- **Hooks**: See `hooks/` folder for reusable logic
- **Project Guidelines**: See `CLAUDE.md` in project root

---

## 🤝 Contributing

### Adding New Components

1. Create folder: `components/MyComponent/`
2. Add files:
   - `MyComponent.jsx` (component)
   - `MyComponent.module.css` (styles)
   - `index.js` (export)
3. Follow naming conventions (PascalCase for components)
4. Use CSS Modules for styling
5. Add PropTypes for type checking
6. Document props and usage in this README

### Code Review Checklist

- [ ] Component uses functional syntax (not class)
- [ ] Styles use CSS Modules (not inline)
- [ ] Props are documented
- [ ] Accessibility features included
- [ ] Error states handled
- [ ] Loading states handled
- [ ] Mobile responsive
- [ ] Follows design system colors/spacing

---

**Last Updated**: 2025-10-25
**Maintained By**: Developer 3 (Frontend Lead)
