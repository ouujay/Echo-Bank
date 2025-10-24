import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [conversation, setConversation] = useState([])
  const [isProcessing, setIsProcessing] = useState(false)

  // Simulated voice interaction
  const handleVoiceClick = () => {
    if (!isListening) {
      setIsListening(true)
      // Simulate listening
      setTimeout(() => {
        setIsListening(false)
        setIsProcessing(true)

        // Simulate processing
        setTimeout(() => {
          const userMessage = "Send 5,000 naira to John"
          const botResponse = "Sending ₦5,000 to John Okafor. Please say your PIN to continue."

          setConversation(prev => [
            ...prev,
            { type: 'user', text: userMessage },
            { type: 'bot', text: botResponse }
          ])
          setIsProcessing(false)
        }, 1500)
      }, 2000)
    }
  }

  return (
    <div className="app">
      {/* Hero Section */}
      <div className="hero">
        <div className="container">
          <div className="hero-content">
            <div className="logo-section">
              <div className="logo-icon">🎙️</div>
              <h1 className="logo-text">EchoBank</h1>
            </div>
            <p className="tagline">
              Voice-Powered Banking for Everyone
            </p>
            <p className="description">
              Perform transactions naturally through voice. Designed for accessibility,
              powered by AI, secured by enterprise-grade technology.
            </p>

            {/* Voice Button */}
            <div className="voice-section">
              <button
                className={`voice-button ${isListening ? 'listening' : ''} ${isProcessing ? 'processing' : ''}`}
                onClick={handleVoiceClick}
                disabled={isProcessing}
              >
                <div className="voice-button-inner">
                  {isProcessing ? (
                    <div className="processing-spinner"></div>
                  ) : (
                    <>
                      <div className="mic-icon">🎤</div>
                      {isListening && (
                        <div className="pulse-rings">
                          <div className="pulse-ring"></div>
                          <div className="pulse-ring"></div>
                          <div className="pulse-ring"></div>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </button>
              <p className="voice-hint">
                {isListening ? 'Listening...' : isProcessing ? 'Processing...' : 'Tap to speak'}
              </p>
            </div>

            {/* Conversation Display */}
            {conversation.length > 0 && (
              <div className="conversation-panel">
                <div className="conversation-header">
                  <span>Conversation</span>
                  <button
                    className="clear-btn"
                    onClick={() => setConversation([])}
                  >
                    Clear
                  </button>
                </div>
                <div className="messages">
                  {conversation.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.type}`}>
                      <div className="message-avatar">
                        {msg.type === 'user' ? '👤' : '🤖'}
                      </div>
                      <div className="message-bubble">
                        <p>{msg.text}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="features">
        <div className="container">
          <h2 className="section-title">Why EchoBank?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🔒</div>
              <h3>Bank-Grade Security</h3>
              <p>Voice PIN + JWT authentication with device binding</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3>Smart Recognition</h3>
              <p>95%+ intent accuracy with natural language processing</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">♿</div>
              <h3>Accessibility First</h3>
              <p>Designed for visually impaired and elderly users</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Lightning Fast</h3>
              <p>Sub-3 second response times for all transactions</p>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="stats">
        <div className="container">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">52M+</div>
              <div className="stat-label">Target Users</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">95%</div>
              <div className="stat-label">Accuracy</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">&lt;3s</div>
              <div className="stat-label">Response Time</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">13</div>
              <div className="stat-label">Edge Cases Handled</div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p>Built with ❤️ for inclusive banking in Nigeria | TIC Hackathon 2025</p>
          <p className="footer-links">
            <a href="https://github.com/ouujay/Echo-Bank" target="_blank" rel="noopener noreferrer">
              GitHub
            </a>
            {' • '}
            <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
              API Docs
            </a>
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
