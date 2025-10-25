import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import './CompanyLogin.css'

function CompanyLogin() {
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })

  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${API_URL}/api/v1/companies/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })

      const data = await response.json()

      if (response.ok) {
        // Store company info in localStorage
        localStorage.setItem('company_id', data.company_id)
        localStorage.setItem('company_name', data.company_name)
        localStorage.setItem('company_email', data.email)

        // Redirect to configure endpoints page
        navigate(`/company/${data.company_id}/configure`)
      } else {
        setError(data.detail?.error || data.detail || 'Login failed')
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
    <div className="login-page-wrapper">
      {/* Header */}
      <header className="page-header">
        <div className="header-container">
          <Link to="/" className="logo-link">
            <span className="logo-text">EchoBank</span>
          </Link>
          <Link to="/" className="back-link">← Back to Home</Link>
        </div>
      </header>

      <div className="login-page">
        <div className="login-container">
          <div className="login-header">
            <h1>Company Login</h1>
            <p>Access your EchoBank dashboard</p>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
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
              <label htmlFor="password">Password *</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter your password"
                required
              />
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'Logging in...' : 'Login'}
            </button>

            <p className="signup-link">
              Don't have an account? <Link to="/register">Register here</Link>
            </p>
          </form>
        </div>

        <div className="login-info">
          <h3>Company Portal Features:</h3>
          <ul>
            <li>Configure API endpoints</li>
            <li>View integration status</li>
            <li>Monitor API usage</li>
            <li>Manage authentication</li>
            <li>Access documentation</li>
            <li>Get technical support</li>
          </ul>

          <div className="help-note">
            <h4>Need Help?</h4>
            <p>Contact support@echobank.com for assistance.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CompanyLogin
