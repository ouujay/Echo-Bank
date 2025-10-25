import { useState } from 'react'
import { Link } from 'react-router-dom'
import './CompanySignup.css'

function CompanySignup() {
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  const [formData, setFormData] = useState({
    company_name: '',
    email: '',
    contact_person: '',
    phone: '',
    password: ''
  })

  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch(`${API_URL}/api/v1/companies/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })

      const data = await response.json()

      if (response.ok) {
        setResult(data)
        // Clear form
        setFormData({
          company_name: '',
          email: '',
          contact_person: '',
          phone: '',
          password: ''
        })
      } else {
        setError(data.detail || 'Registration failed')
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

  return (
    <div className="signup-page-wrapper">
      {/* Header */}
      <header className="page-header">
        <div className="header-container">
          <Link to="/" className="logo-link">
            <span className="logo-text">EchoBank</span>
          </Link>
          <Link to="/" className="back-link">← Back to Home</Link>
        </div>
      </header>

      <div className="signup-page">
        <div className="signup-container">
          <div className="signup-header">
            <h1>Register Your Bank</h1>
            <p>Add voice intelligence to your banking app in minutes</p>
          </div>

          {!result ? (
            <form onSubmit={handleSubmit} className="signup-form">
            <div className="form-group">
              <label htmlFor="company_name">Bank/Company Name *</label>
              <input
                type="text"
                id="company_name"
                name="company_name"
                value={formData.company_name}
                onChange={handleChange}
                placeholder="e.g., Zenith Bank"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Company Email *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="api@yourbank.com"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="contact_person">Contact Person *</label>
              <input
                type="text"
                id="contact_person"
                name="contact_person"
                value={formData.contact_person}
                onChange={handleChange}
                placeholder="John Doe"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="phone">Phone Number *</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                placeholder="+234123456789"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password *</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Create a secure password"
                required
              />
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'Registering...' : 'Register Company'}
            </button>

            <p className="signup-note">
              By registering, you agree to our Terms of Service and Privacy Policy
            </p>

            <p className="login-link">
              Already have an account? <Link to="/login">Login here</Link>
            </p>
            </form>
          ) : (
            <div className="success-result">
              <div className="success-icon">✓</div>
              <h2>Registration Successful!</h2>

              <div className="result-details">
                <div className="result-item">
                  <span className="label">Company ID:</span>
                  <span className="value">{result.company_id}</span>
                </div>

                <div className="result-item">
                  <span className="label">Company Name:</span>
                  <span className="value">{result.company_name}</span>
                </div>

                <div className="result-item api-key">
                  <span className="label">API Key:</span>
                  <div className="api-key-box">
                    <code>{result.api_key}</code>
                    <button
                      className="copy-btn"
                      onClick={() => {
                        navigator.clipboard.writeText(result.api_key)
                        alert('API Key copied!')
                      }}
                    >
                      Copy
                    </button>
                  </div>
                </div>

                <div className="warning-box">
                  <strong>⚠️ IMPORTANT:</strong> Save your API key now! You won't be able to see it again.
                </div>
              </div>

              <div className="next-steps">
                <h3>Next Steps:</h3>
                <ol>
                  <li>Save your API key in a secure location</li>
                  <li>Configure your API endpoints</li>
                  <li>Test the integration</li>
                  <li>Go live!</li>
                </ol>

                <a href={`/company/${result.company_id}/configure`} className="configure-btn">
                  Configure Endpoints
                </a>
              </div>
            </div>
          )}
        </div>

        <div className="signup-info">
          <h3>What You Get:</h3>
          <ul>
            <li>Voice-powered banking for your customers</li>
            <li>Natural language understanding</li>
            <li>Secure PIN verification</li>
            <li>Multi-language support</li>
            <li>24/7 API access</li>
            <li>Detailed analytics dashboard</li>
          </ul>

          <div className="pricing-note">
            <h4>Pricing</h4>
            <p>Contact sales@echobank.com for custom pricing based on your usage.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CompanySignup
