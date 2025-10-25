# EchoBank Voice Widget

**Plug-and-play voice banking for your React application**

Add natural language voice commands to your banking app in under 5 minutes.

---

## 📦 Installation

### Step 1: Download Files

Download these 2 files from your EchoBank dashboard:
- `EchoBankVoiceWidget.jsx`
- `EchoBankVoiceWidget.css`

Place them in your project (e.g., `src/components/`):

```
your-app/
├── src/
│   ├── components/
│   │   ├── EchoBankVoiceWidget.jsx  ← Downloaded from EchoBank
│   │   └── EchoBankVoiceWidget.css  ← Downloaded from EchoBank
│   └── App.js
```

### Step 2: Import and Use

```jsx
import { useState } from 'react';
import EchoBankVoiceWidget from './components/EchoBankVoiceWidget';
import './components/EchoBankVoiceWidget.css';

function App() {
  const [showVoice, setShowVoice] = useState(false);

  // Get from your auth context
  const userAccount = user.accounts[0].account_number;  // e.g., "0634250390"
  const userToken = localStorage.getItem('token');       // User's JWT

  return (
    <div className="app">
      {/* Your existing app content */}

      {/* Voice Banking Button */}
      <button onClick={() => setShowVoice(true)}>
        🎤 Voice Banking
      </button>

      {/* Voice Widget */}
      {showVoice && (
        <EchoBankVoiceWidget
          companyId="YOUR_COMPANY_ID"      // From EchoBank dashboard
          accountNumber={userAccount}
          userToken={userToken}
          onClose={() => setShowVoice(false)}
        />
      )}
    </div>
  );
}
```

---

## ⚙️ Configuration

### Required Props

| Prop | Type | Description |
|------|------|-------------|
| `companyId` | `string` | Your EchoBank company ID (from dashboard) |
| `accountNumber` | `string` | User's bank account number |
| `userToken` | `string` | User's JWT authentication token |
| `onClose` | `function` | Callback when modal is closed |

### Optional Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `echoBankApiUrl` | `string` | `http://localhost:8000` | EchoBank API URL (change for production) |

---

## 🎯 Example: Full Integration

```jsx
import { useState } from 'react';
import EchoBankVoiceWidget from './components/EchoBankVoiceWidget';
import './components/EchoBankVoiceWidget.css';

function Dashboard() {
  const [showVoiceModal, setShowVoiceModal] = useState(false);

  // Get user data from your auth context/state
  const user = useAuth();  // or however you manage auth

  return (
    <div className="dashboard">
      <h1>Welcome, {user.name}</h1>
      <p>Account: {user.account_number}</p>

      {/* Voice Banking Button */}
      <button
        onClick={() => setShowVoiceModal(true)}
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          width: '64px',
          height: '64px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #0066FF, #0052CC)',
          color: 'white',
          border: 'none',
          fontSize: '28px',
          cursor: 'pointer',
          boxShadow: '0 8px 20px rgba(0, 102, 255, 0.3)',
        }}
      >
        🎤
      </button>

      {/* Voice Widget */}
      {showVoiceModal && (
        <EchoBankVoiceWidget
          companyId="5"  // Your company ID
          accountNumber={user.account_number}
          userToken={user.token}
          onClose={() => setShowVoiceModal(false)}
          echoBankApiUrl="https://api.echobank.com"  // Production URL
        />
      )}
    </div>
  );
}
```

---

## 🎙️ What Users Can Say

Once integrated, your users can use voice commands like:

### Check Balance
- "What's my balance?"
- "How much money do I have?"
- "Check my account balance"

### Send Money
- "Send 5000 to John"
- "Transfer 10000 naira to Sarah"
- "Send money to Mary"

### View Recipients
- "Show my beneficiaries"
- "List my recipients"
- "Who can I send money to?"

### View Transactions
- "Show my transactions"
- "Transaction history"
- "Recent transfers"

---

## 🔧 Production Setup

### Update API URL

For production, change the `echoBankApiUrl`:

```jsx
<EchoBankVoiceWidget
  companyId="5"
  accountNumber={user.account_number}
  userToken={user.token}
  onClose={() => setShowVoiceModal(false)}
  echoBankApiUrl="https://api.echobank.com"  // ← Production URL
/>
```

### Environment Variables (Recommended)

```javascript
// .env
REACT_APP_ECHOBANK_API_URL=https://api.echobank.com
REACT_APP_ECHOBANK_COMPANY_ID=5

// In your code
<EchoBankVoiceWidget
  companyId={process.env.REACT_APP_ECHOBANK_COMPANY_ID}
  accountNumber={user.account_number}
  userToken={user.token}
  onClose={() => setShowVoiceModal(false)}
  echoBankApiUrl={process.env.REACT_APP_ECHOBANK_API_URL}
/>
```

---

## 🎨 Customization

### Custom Button Style

The widget provides the modal UI. You design the trigger button:

```jsx
// Example: Floating action button
<button
  onClick={() => setShowVoice(true)}
  style={{
    position: 'fixed',
    bottom: '20px',
    right: '20px',
    width: '60px',
    height: '60px',
    borderRadius: '50%',
    background: 'your-brand-color',
    // ... your styles
  }}
>
  🎤
</button>

// Example: In-page button
<button
  onClick={() => setShowVoice(true)}
  className="your-button-class"
>
  Use Voice Banking
</button>
```

### Modal Styling

The widget uses scoped CSS classes (`echobank-*`) to avoid conflicts. To customize colors, override these CSS variables:

```css
/* In your app's CSS */
.echobank-voice-modal {
  /* Override primary color */
  --echobank-primary: #YOUR_BRAND_COLOR;
}
```

---

## 🐛 Troubleshooting

### Microphone Not Working

**Issue**: "Permission denied" error

**Solution**: Ensure your app is served over HTTPS (required for microphone access):
```
http://localhost:3000  ✅ OK (development)
https://yourbank.com   ✅ OK (production)
http://yourbank.com    ❌ Not allowed (production must use HTTPS)
```

---

### No Audio Response

**Issue**: Transcript works but no voice response

**Solution**: Check `include_audio=true` is set (it's default in the widget)

---

### CORS Error

**Issue**: "Cross-Origin Request Blocked"

**Solution**: Contact EchoBank support to whitelist your domain. Provide:
- Your domain (e.g., https://yourbank.com)
- Your company ID

---

## 📞 Support

**Questions? Issues?**
- Dashboard: Log in at https://echobank.com/login
- Email: support@echobank.com
- Documentation: https://docs.echobank.com

---

## 🔐 Security Best Practices

### ✅ DO:
- Always use HTTPS in production
- Validate `userToken` on your backend
- Store company ID in environment variables
- Keep user tokens secure (HttpOnly cookies recommended)

### ❌ DON'T:
- Expose API keys in frontend code
- Use HTTP in production
- Store tokens in localStorage (use secure cookies if possible)
- Share your company ID publicly

---

## 📄 License

This widget is provided under the EchoBank API Terms of Service.

By using this widget, you agree to:
- Maintain EchoBank branding ("Powered by EchoBank" footer)
- Follow security best practices
- Comply with voice banking regulations in your jurisdiction

---

## 🎉 That's It!

You now have voice banking in your app! Your users can speak naturally to:
- ✅ Check balances
- ✅ Send money
- ✅ View recipients
- ✅ View transactions

**All with natural language!** 🚀

---

**Need help?** Contact us at support@echobank.com
