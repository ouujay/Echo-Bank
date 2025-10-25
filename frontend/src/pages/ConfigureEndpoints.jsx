import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import './ConfigureEndpoints.css'

function ConfigureEndpoints() {
  const { companyId } = useParams()
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  const [formData, setFormData] = useState({
    base_url: '',
    auth_type: 'bearer',
    auth_header_name: 'Authorization',
    get_balance_endpoint: '/api/v1/accounts/{account_number}/balance',
    get_recipients_endpoint: '/api/v1/accounts/{account_number}/beneficiaries',
    initiate_transfer_endpoint: '/api/v1/transfers/initiate',
    confirm_transfer_endpoint: '/api/v1/transfers/{transfer_id}/confirm',
    verify_pin_endpoint: '/api/v1/auth/verify-pin',
    get_transactions_endpoint: '',
    add_recipient_endpoint: '',
    cancel_transfer_endpoint: ''
  })

  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [companyInfo, setCompanyInfo] = useState(null)

  useEffect(() => {
    // Load company info
    fetch(`${API_URL}/api/v1/companies/${companyId}`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setCompanyInfo(data.data)
        }
      })
      .catch(err => console.error(err))

    // Load existing endpoints if any
    fetch(`${API_URL}/api/v1/companies/${companyId}/endpoints`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          // Map the backend response to frontend form structure
          const backendData = data.data
          setFormData(prev => ({
            ...prev,
            base_url: backendData.base_url || prev.base_url,
            auth_type: backendData.auth_type || prev.auth_type,
            auth_header_name: backendData.auth_header_name || prev.auth_header_name,
            get_balance_endpoint: backendData.endpoints?.get_balance || prev.get_balance_endpoint,
            get_recipients_endpoint: backendData.endpoints?.get_recipients || prev.get_recipients_endpoint,
            initiate_transfer_endpoint: backendData.endpoints?.initiate_transfer || prev.initiate_transfer_endpoint,
            confirm_transfer_endpoint: backendData.endpoints?.confirm_transfer || prev.confirm_transfer_endpoint,
            verify_pin_endpoint: backendData.endpoints?.verify_pin || prev.verify_pin_endpoint,
            get_transactions_endpoint: backendData.endpoints?.get_transactions || prev.get_transactions_endpoint,
            add_recipient_endpoint: backendData.endpoints?.add_recipient || prev.add_recipient_endpoint,
            cancel_transfer_endpoint: backendData.endpoints?.cancel_transfer || prev.cancel_transfer_endpoint
          }))
        }
      })
      .catch(err => console.log('No existing endpoints'))
  }, [companyId, API_URL])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch(`${API_URL}/api/v1/companies/${companyId}/endpoints`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })

      const data = await response.json()

      if (response.ok) {
        setResult(data)
      } else {
        setError(data.detail || 'Configuration failed')
      }
    } catch (err) {
      setError('Network error. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleLogout = () => {
    // Clear company info from localStorage
    localStorage.removeItem('company_id')
    localStorage.removeItem('company_name')
    localStorage.removeItem('company_email')
    // Redirect to home
    window.location.href = '/'
  }

  const generateIntegrationGuide = (company) => {
    if (!company) return '';

    return `# EchoBank Voice Integration Guide

**Company:** ${company.company_name}
**Company ID:** ${company.company_id}
**Date:** ${new Date().toLocaleDateString()}

---

## 🎯 Quick Start

Your company has been registered with EchoBank. Follow this guide to integrate voice banking into your application.

### Your EchoBank Voice API

**Endpoint:** \`http://localhost:8000/api/v1/voice/process-audio\`
**Company ID:** \`${company.company_id}\`

---

## 📋 Integration Steps

### Step 1: Add Voice Button to Your App

\`\`\`javascript
// In your dashboard/main page
const handleVoiceClick = async () => {
  // Start recording audio
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mediaRecorder = new MediaRecorder(stream);

  // ... recording logic
};
\`\`\`

### Step 2: Send Audio to EchoBank

\`\`\`javascript
const formData = new FormData();
formData.append('audio', audioBlob);

const response = await fetch(
  'http://localhost:8000/api/v1/voice/process-audio?include_audio=true',
  {
    method: 'POST',
    headers: {
      'account-number': userAccount,
      'company-id': '${company.company_id}',
      'session-id': sessionId,
      'token': userAuthToken,
    },
    body: formData
  }
);

const result = await response.json();
// result.response_text = what to say back
// result.response_audio = TTS audio (base64)
\`\`\`

### Step 3: Handle Response

\`\`\`javascript
// Display response
console.log(result.response_text);

// Play audio (if included)
if (result.response_audio) {
  const audio = new Audio(\`data:audio/mp3;base64,\${result.response_audio}\`);
  audio.play();
}
\`\`\`

---

## 🔑 Required Headers

Every request to EchoBank must include:

\`\`\`javascript
{
  'account-number': 'USER_ACCOUNT_NUMBER',  // User's bank account
  'company-id': '${company.company_id}',    // Your company ID
  'session-id': 'unique_session_id',       // Conversation tracking
  'token': 'USER_JWT_TOKEN'                // User's auth token
}
\`\`\`

---

## 🎙️ Supported Commands

Users can say:
- "What's my balance?"
- "Send 5000 to John"
- "Show my beneficiaries"
- "Transfer 10000 naira to Sarah"

EchoBank will:
1. Transcribe the audio
2. Understand the intent
3. Call YOUR API endpoints
4. Return a response

---

## 📞 Support

- Dashboard: http://localhost:5174/login
- Email: ${company.email}
- API Docs: http://localhost:8000/docs

---

Generated by EchoBank | ${new Date().toLocaleDateString()}
`;
  }

  return (
    <>
      {/* Header */}
      <header className="page-header">
        <div className="header-container">
          <Link to="/" className="logo-link">
            <span className="logo-text">EchoBank</span>
          </Link>
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            {companyInfo && (
              <span style={{ color: '#A0AEC0', fontSize: '14px' }}>
                Logged in as <strong style={{ color: '#fff' }}>{companyInfo.company_name}</strong>
              </span>
            )}
            <button
              onClick={handleLogout}
              className="back-link"
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: 'inherit',
                fontSize: 'inherit',
                padding: 0
              }}
            >
              Logout →
            </button>
          </div>
        </div>
      </header>

      <div className="configure-page">
        <div className="configure-header">
          <h1>Configure API Endpoints</h1>
          {companyInfo && (
            <p>Company: <strong>{companyInfo.company_name}</strong> (ID: {companyInfo.company_id})</p>
          )}
        </div>

        {/* Integration Guide Banner */}
        {result && (
          <div className="integration-guide-banner">
            <div className="banner-content">
              <h3>🎉 Configuration Saved!</h3>
              <p>Your endpoints are configured. Now integrate voice banking into your app:</p>
              <div className="guide-links">
                <a href="#integration-info" className="guide-link-btn primary">
                  📖 View Integration Guide
                </a>
                <a
                  href={`data:text/markdown;charset=utf-8,${encodeURIComponent(generateIntegrationGuide(companyInfo))}`}
                  download={`EchoBank_Integration_Guide_${companyInfo?.company_name?.replace(/\s+/g, '_')}.md`}
                  className="guide-link-btn secondary"
                >
                  📥 Download Guide
                </a>
              </div>
            </div>
          </div>
        )}

      <div className="configure-container">
        <div className="config-instructions">
          <h2>How This Works</h2>
          <p>
            Tell EchoBank where YOUR banking API endpoints are located. When your users speak,
            we'll call these endpoints with their authentication token to perform actions.
          </p>

          <div className="instruction-steps">
            <div className="step">
              <span className="step-number">1</span>
              <div>
                <h4>Base URL</h4>
                <p>Your API's base URL (e.g., https://api.yourbank.com)</p>
              </div>
            </div>

            <div className="step">
              <span className="step-number">2</span>
              <div>
                <h4>Authentication</h4>
                <p>How we should authenticate with your API</p>
              </div>
            </div>

            <div className="step">
              <span className="step-number">3</span>
              <div>
                <h4>Endpoints</h4>
                <p>Specific paths for each banking operation</p>
              </div>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="config-form">
          <div className="form-section">
            <h3>Base Configuration</h3>

            <div className="form-group">
              <label htmlFor="base_url">Base URL *</label>
              <input
                type="url"
                id="base_url"
                name="base_url"
                value={formData.base_url}
                onChange={handleChange}
                placeholder="https://api.yourbank.com"
                required
              />
              <span className="help-text">Your API's base URL</span>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="auth_type">Auth Type *</label>
                <select
                  id="auth_type"
                  name="auth_type"
                  value={formData.auth_type}
                  onChange={handleChange}
                  required
                >
                  <option value="bearer">Bearer Token</option>
                  <option value="api_key">API Key</option>
                  <option value="basic">Basic Auth</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="auth_header_name">Auth Header Name *</label>
                <input
                  type="text"
                  id="auth_header_name"
                  name="auth_header_name"
                  value={formData.auth_header_name}
                  onChange={handleChange}
                  placeholder="Authorization"
                  required
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Required Endpoints</h3>

            <div className="form-group">
              <label htmlFor="get_balance_endpoint">Get Balance Endpoint *</label>
              <input
                type="text"
                id="get_balance_endpoint"
                name="get_balance_endpoint"
                value={formData.get_balance_endpoint}
                onChange={handleChange}
                placeholder="/api/v1/accounts/{account_number}/balance"
                required
              />
              <span className="help-text">Use {'{account_number}'} as placeholder</span>
            </div>

            <div className="form-group">
              <label htmlFor="get_recipients_endpoint">Get Recipients Endpoint *</label>
              <input
                type="text"
                id="get_recipients_endpoint"
                name="get_recipients_endpoint"
                value={formData.get_recipients_endpoint}
                onChange={handleChange}
                placeholder="/api/v1/accounts/{account_number}/beneficiaries"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="initiate_transfer_endpoint">Initiate Transfer Endpoint *</label>
              <input
                type="text"
                id="initiate_transfer_endpoint"
                name="initiate_transfer_endpoint"
                value={formData.initiate_transfer_endpoint}
                onChange={handleChange}
                placeholder="/api/v1/transfers/initiate"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirm_transfer_endpoint">Confirm Transfer Endpoint *</label>
              <input
                type="text"
                id="confirm_transfer_endpoint"
                name="confirm_transfer_endpoint"
                value={formData.confirm_transfer_endpoint}
                onChange={handleChange}
                placeholder="/api/v1/transfers/{transfer_id}/confirm"
                required
              />
              <span className="help-text">Use {'{transfer_id}'} as placeholder</span>
            </div>

            <div className="form-group">
              <label htmlFor="verify_pin_endpoint">Verify PIN Endpoint *</label>
              <input
                type="text"
                id="verify_pin_endpoint"
                name="verify_pin_endpoint"
                value={formData.verify_pin_endpoint}
                onChange={handleChange}
                placeholder="/api/v1/auth/verify-pin"
                required
              />
            </div>
          </div>

          <div className="form-section">
            <h3>Optional Endpoints</h3>

            <div className="form-group">
              <label htmlFor="get_transactions_endpoint">Get Transactions Endpoint</label>
              <input
                type="text"
                id="get_transactions_endpoint"
                name="get_transactions_endpoint"
                value={formData.get_transactions_endpoint}
                onChange={handleChange}
                placeholder="/api/v1/transactions"
              />
            </div>

            <div className="form-group">
              <label htmlFor="add_recipient_endpoint">Add Recipient Endpoint</label>
              <input
                type="text"
                id="add_recipient_endpoint"
                name="add_recipient_endpoint"
                value={formData.add_recipient_endpoint}
                onChange={handleChange}
                placeholder="/api/v1/beneficiaries"
              />
            </div>

            <div className="form-group">
              <label htmlFor="cancel_transfer_endpoint">Cancel Transfer Endpoint</label>
              <input
                type="text"
                id="cancel_transfer_endpoint"
                name="cancel_transfer_endpoint"
                value={formData.cancel_transfer_endpoint}
                onChange={handleChange}
                placeholder="/api/v1/transfers/{transfer_id}/cancel"
              />
            </div>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {result && (
            <div className="success-message">
              Configuration saved successfully! Your company is now active.
            </div>
          )}

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Saving...' : 'Save Configuration'}
          </button>
        </form>

        {/* Integration Info Section */}
        {companyInfo && (
          <div id="integration-info" className="integration-info-section">
            <h2>📖 Integration Information</h2>

            <div className="info-card">
              <h3>Your EchoBank Voice API</h3>
              <div className="info-item">
                <span className="info-label">Endpoint:</span>
                <code className="info-value">http://localhost:8000/api/v1/voice/process-audio</code>
              </div>
              <div className="info-item">
                <span className="info-label">Company ID:</span>
                <code className="info-value">{companyInfo.company_id}</code>
              </div>
            </div>

            <div className="info-card">
              <h3>Required Headers</h3>
              <pre className="code-block">{`{
  'account-number': 'USER_ACCOUNT_NUMBER',
  'company-id': '${companyInfo.company_id}',
  'session-id': 'unique_session_id',
  'token': 'USER_JWT_TOKEN'
}`}</pre>
            </div>

            <div className="info-card">
              <h3>Example Request</h3>
              <pre className="code-block">{`const formData = new FormData();
formData.append('audio', audioBlob);

const response = await fetch(
  'http://localhost:8000/api/v1/voice/process-audio?include_audio=true',
  {
    method: 'POST',
    headers: {
      'account-number': userAccount,
      'company-id': '${companyInfo.company_id}',
      'session-id': sessionId,
      'token': userAuthToken,
    },
    body: formData
  }
);`}</pre>
            </div>

            <div className="info-card">
              <h3>📥 Download Voice Widget</h3>
              <p>Get our ready-to-use React component. Just drop it into your app and you're done!</p>

              <div className="widget-download-options">
                <a href="/widget/EchoBankVoiceWidget.jsx" download className="download-widget-btn">
                  📄 Download Component (.jsx)
                </a>
                <a href="/widget/EchoBankVoiceWidget.css" download className="download-widget-btn">
                  🎨 Download Styles (.css)
                </a>
                <a href="/widget/README.md" download className="download-widget-btn">
                  📖 Download Instructions
                </a>
              </div>

              <div style={{ marginTop: '16px', padding: '12px', background: '#F7FAFC', borderRadius: '8px', fontSize: '13px', color: '#4A5568' }}>
                <strong>Quick Start:</strong> Download all 3 files, place them in your <code>src/components/</code> folder, and use with just 3 props!
              </div>
            </div>

            <div className="info-card">
              <h3>📥 Download Integration Guide</h3>
              <p>Get the full integration guide with detailed examples and code snippets.</p>
              <a
                href={`data:text/markdown;charset=utf-8,${encodeURIComponent(generateIntegrationGuide(companyInfo))}`}
                download={`EchoBank_Integration_Guide_${companyInfo?.company_name?.replace(/\s+/g, '_')}.md`}
                className="download-guide-btn"
              >
                📥 Download Integration Guide
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
    </>
  )
}

export default ConfigureEndpoints
