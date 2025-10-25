import { useState, useRef, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import './App.css'
import './VoiceModalPremium.css'
import CompanySignup from './pages/CompanySignup'
import CompanyLogin from './pages/CompanyLogin'
import ConfigureEndpoints from './pages/ConfigureEndpoints'

function LandingPage() {
  const ECHOBANK_API = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1`
  const DEMO_ACCOUNT = '6523711418'  // Demo Bank account (John Doe)

  const [showVoiceDemo, setShowVoiceDemo] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [conversation, setConversation] = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [audioUrl, setAudioUrl] = useState(null)

  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const audioRef = useRef(null)
  const recordingDelayTimeoutRef = useRef(null)
  const conversationEndRef = useRef(null)

  // Auto-scroll to latest message when conversation updates
  useEffect(() => {
    if (conversationEndRef.current) {
      conversationEndRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'end'
      })
    }
  }, [conversation])

  // Start voice recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        await sendAudioToEchoBank(audioBlob)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Error starting recording:', error)
      alert('Could not access microphone. Please check permissions.')
    }
  }

  // Stop voice recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  // Send audio to EchoBank API
  const sendAudioToEchoBank = async (audioBlob) => {
    setIsProcessing(true)

    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.webm')

      const currentSessionId = sessionId || `demo_session_${Date.now()}`

      const response = await fetch(`${ECHOBANK_API}/voice/process-audio`, {
        method: 'POST',
        headers: {
          'account-number': DEMO_ACCOUNT,
          'company-id': '4',  // Demo Bank company ID
          'session-id': currentSessionId,
          'token': 'demo_token_123',  // Demo token for testing
          'include-audio': 'true'  // Request TTS audio response
        },
        body: formData
      })

      const result = await response.json()

      console.log('[ECHOBANK DEBUG] API Response:', result)

      if (result.session_id) {
        setSessionId(result.session_id)
      }

      // Extract transcript from Whisper response if audio processing succeeded
      const userMsg = {
        type: 'user',
        text: result.transcript || result.text || 'Voice command',
        timestamp: new Date()
      }

      const botMsg = {
        type: 'bot',
        text: result.response_text || 'Processing...',
        intent: result.intent,
        timestamp: new Date(),
        audio: result.response_audio
      }

      setConversation(prev => [...prev, userMsg, botMsg])

      // Play audio response if available
      if (result.response_audio) {
        console.log('[ECHOBANK DEBUG] Playing TTS audio...')
        playAudioResponse(result.response_audio)
      } else {
        console.warn('[ECHOBANK WARNING] No response_audio in result. TTS not enabled.')
      }

    } catch (error) {
      console.error('Error processing audio:', error)
      setConversation(prev => [...prev, {
        type: 'bot',
        text: 'Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date()
      }])
    } finally {
      setIsProcessing(false)
    }
  }

  // Stop any playing audio
  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      setIsSpeaking(false)
    }
  }

  // Play audio response
  const playAudioResponse = (base64Audio) => {
    try {
      // Support both WAV (pyttsx3) and MP3 (OpenAI TTS)
      const audioData = `data:audio/wav;base64,${base64Audio}`
      setAudioUrl(audioData)

      if (audioRef.current) {
        audioRef.current.src = audioData
        setIsSpeaking(true)

        // Play and handle events
        audioRef.current.play()

        // When audio finishes playing
        audioRef.current.onended = () => {
          setIsSpeaking(false)
        }

        // Handle errors
        audioRef.current.onerror = () => {
          console.error('Error playing audio')
          setIsSpeaking(false)
        }
      }
    } catch (error) {
      console.error('Error playing audio:', error)
      setIsSpeaking(false)
    }
  }

  // Handle voice button click
  const handleVoiceClick = async () => {
    if (!showVoiceDemo) {
      setShowVoiceDemo(true)
      return
    }

    // If currently recording, stop it
    if (isRecording) {
      stopRecording()
      return
    }

    // If audio is playing, stop it
    if (isSpeaking) {
      stopAudio()
    }

    // Clear any existing timeout
    if (recordingDelayTimeoutRef.current) {
      clearTimeout(recordingDelayTimeoutRef.current)
    }

    // Wait 2 seconds before starting recording (so it doesn't pick up its own voice)
    setIsProcessing(true) // Show "waiting" state

    recordingDelayTimeoutRef.current = setTimeout(async () => {
      setIsProcessing(false)
      await startRecording()
    }, 2000) // 2 second delay
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container">
          <div className="header-content">
            <Link to="/" className="logo">
              <img src="/echobank-logo.png" alt="EchoBank" className="logo-image" />
              <span className="logo-text">EchoBank</span>
            </Link>

            {/* Desktop Navigation */}
            <nav className="desktop-nav">
              <a href="#features" className="nav-link">Features</a>
              <a href="#how-it-works" className="nav-link">How It Works</a>
              <a href="#api-docs" className="nav-link">API Docs</a>
            </nav>

            {/* Right Side Actions */}
            <div className="header-right">
              <Link to="/login" className="btn-secondary btn-login" style={{ marginRight: '12px', textDecoration: 'none' }}>
                Login
              </Link>
              <Link to="/signup" className="btn-primary btn-signup" style={{ marginRight: '12px', textDecoration: 'none' }}>
                Sign Up
              </Link>
              <button className="btn-primary btn-demo" onClick={() => setShowVoiceDemo(true)}>
                Try Demo
              </button>

              {/* Hamburger Menu */}
              <button
                className={`hamburger ${mobileMenuOpen ? 'active' : ''}`}
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                aria-label="Toggle menu"
              >
                <span></span>
                <span></span>
                <span></span>
              </button>
            </div>
          </div>

          {/* Mobile Navigation */}
          <nav className={`mobile-nav ${mobileMenuOpen ? 'open' : ''}`}>
            <a href="#features" className="mobile-nav-link" onClick={() => setMobileMenuOpen(false)}>Features</a>
            <a href="#how-it-works" className="mobile-nav-link" onClick={() => setMobileMenuOpen(false)}>How It Works</a>
            <a href="#api-docs" className="mobile-nav-link" onClick={() => setMobileMenuOpen(false)}>API Docs</a>
            <div className="mobile-nav-divider"></div>
            <Link to="/login" className="mobile-nav-link mobile-nav-button" onClick={() => setMobileMenuOpen(false)}>Login</Link>
            <Link to="/signup" className="mobile-nav-link mobile-nav-button primary" onClick={() => setMobileMenuOpen(false)}>Sign Up</Link>
            <button className="mobile-nav-link mobile-nav-button primary" onClick={() => { setShowVoiceDemo(true); setMobileMenuOpen(false); }}>Try Demo</button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="main-content">
        <div className="container">
          <section className="hero-section">
            <div className="hero-content">
              <div className="hero-image">
                <img src="/hero-image.png" alt="Person using voice banking on mobile phone" />
              </div>
              <div className="hero-text">
                <h1 className="hero-title">
                  Voice-Powered Banking<br />For Everyone
                </h1>
                <p className="hero-subtitle">
                  EchoBank is an AI-powered voice API that brings natural voice interactions
                  to banking apps. Enable your customers to check balances, send money, and
                  manage accounts using just their voice.
                </p>
                <div className="hero-actions">
                  <button className="btn-hero" onClick={() => setShowVoiceDemo(true)}>
                    Try Voice Demo
                  </button>
                  <a href="#api-docs" className="btn-secondary">
                    View API Docs
                  </a>
                </div>
                <p className="hero-note">
                  Designed for visually impaired, elderly, and low-literacy users
                </p>
              </div>
            </div>
          </section>

          {/* Features Section */}
          <section id="features" className="features-section">
            <h2 className="section-title-center">Why EchoBank?</h2>
            <p className="section-subtitle-center">
              Add voice intelligence to your banking app in minutes
            </p>

            <div className="features-grid">
              <div className="feature-card">
                <h3 className="feature-title">Intent Recognition</h3>
                <p className="feature-description">
                  Understands natural language: "Send 5000 to John" automatically
                  detects recipient and amount.
                </p>
              </div>

              <div className="feature-card">
                <h3 className="feature-title">Text-to-Speech</h3>
                <p className="feature-description">
                  Responds with natural voice: "Your balance is 45,000 naira."
                  No screen reading required.
                </p>
              </div>

              <div className="feature-card">
                <h3 className="feature-title">Secure by Default</h3>
                <p className="feature-description">
                  PIN verification, session management, and encryption built-in.
                  We never store your user data.
                </p>
              </div>

              <div className="feature-card">
                <h3 className="feature-title">Fast Integration</h3>
                <p className="feature-description">
                  One API endpoint. Send audio, get intent + action.
                  Works with your existing backend.
                </p>
              </div>

              <div className="feature-card">
                <h3 className="feature-title">Multi-Language</h3>
                <p className="feature-description">
                  Supports Nigerian English, Pidgin, and local accents.
                  Expanding to more languages soon.
                </p>
              </div>

              <div className="feature-card">
                <h3 className="feature-title">Analytics</h3>
                <p className="feature-description">
                  Track voice usage, intent accuracy, and user satisfaction.
                  Improve accessibility over time.
                </p>
              </div>
            </div>
          </section>

          {/* How It Works */}
          <section id="how-it-works" className="how-it-works-section">
            <h2 className="section-title-center">How It Works</h2>
            <p className="section-subtitle-center">
              3 simple steps to add voice to your app
            </p>

            <div className="steps-grid">
              <div className="step-card">
                <div className="step-number">1</div>
                <h3 className="step-title">User Speaks</h3>
                <p className="step-description">
                  User taps voice button in your app and says:<br />
                  <em>"Send 5000 naira to John"</em>
                </p>
              </div>

              <div className="step-arrow">→</div>

              <div className="step-card">
                <div className="step-number">2</div>
                <h3 className="step-title">Send to EchoBank</h3>
                <p className="step-description">
                  Your app sends audio to EchoBank API:<br />
                  <code>POST /api/v1/voice/process-audio</code>
                </p>
              </div>

              <div className="step-arrow">→</div>

              <div className="step-card">
                <div className="step-number">3</div>
                <h3 className="step-title">Get Response</h3>
                <p className="step-description">
                  Receive intent, action, and voice response:<br />
                  <em>"Sending ₦5,000 to John. Say your PIN."</em>
                </p>
              </div>
            </div>

            <div className="code-example">
              <h4>Integration Example</h4>
              <pre>{`const formData = new FormData();
formData.append('audio', audioBlob);

const response = await fetch('https://api.echobank.com/voice/process-audio', {
  method: 'POST',
  headers: {
    'account_number': userAccount,
    'token': userAuthToken
  },
  body: formData
});

const result = await response.json();
// result.intent = "transfer"
// result.response_text = "Sending ₦5,000 to John..."
// result.response_audio = "base64_audio_data"`}</pre>
            </div>
          </section>

          {/* API Docs Section */}
          <section id="api-docs" className="api-docs-section">
            <h2 className="section-title-center">API Documentation</h2>
            <p className="section-subtitle-center">
              Simple REST API with JSON responses
            </p>

            <div className="api-cards">
              <div className="api-card">
                <div className="api-method">POST</div>
                <h3 className="api-endpoint">/api/v1/voice/process-audio</h3>
                <p className="api-description">
                  Process voice audio and return intent + action
                </p>
                <div className="api-details">
                  <strong>Headers:</strong>
                  <ul>
                    <li><code>account_number</code>: User's account number</li>
                    <li><code>token</code>: Your bank's auth token</li>
                  </ul>
                  <strong>Body:</strong>
                  <ul>
                    <li><code>audio</code>: Audio file (wav/mp3/webm)</li>
                  </ul>
                </div>
              </div>

              <div className="api-card">
                <div className="api-method">POST</div>
                <h3 className="api-endpoint">/api/v1/voice/process-text</h3>
                <p className="api-description">
                  Process text command (for testing or text input)
                </p>
                <div className="api-details">
                  <strong>Body:</strong>
                  <ul>
                    <li><code>text</code>: User command as text</li>
                    <li><code>account_number</code>: User's account</li>
                    <li><code>session_id</code>: Session ID (optional)</li>
                  </ul>
                </div>
              </div>

              <div className="api-card">
                <div className="api-method">POST</div>
                <h3 className="api-endpoint">/api/v1/voice/tts</h3>
                <p className="api-description">
                  Convert text to speech audio
                </p>
                <div className="api-details">
                  <strong>Body:</strong>
                  <ul>
                    <li><code>text</code>: Text to convert to speech</li>
                    <li><code>voice</code>: Voice type (nova/alloy/echo)</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="cta-section">
              <h3>Ready to get started?</h3>
              <p>Contact us for API access and integration support</p>
              <button className="btn-hero">Request API Access</button>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h4>EchoBank</h4>
              <p>Voice-powered banking for everyone</p>
            </div>
            <div className="footer-section">
              <h4>Product</h4>
              <a href="#features">Features</a>
              <a href="#how-it-works">How It Works</a>
              <a href="#api-docs">API Docs</a>
            </div>
            <div className="footer-section">
              <h4>Company</h4>
              <a href="#">About Us</a>
              <a href="#">Contact</a>
              <a href="#">Privacy</a>
            </div>
          </div>
          <div className="footer-bottom">
            <p>© 2025 EchoBank. Built for accessibility and financial inclusion.</p>
          </div>
        </div>
      </footer>

      {/* Voice Demo Modal */}
      {showVoiceDemo && (
        <div className="voice-overlay" onClick={() => setShowVoiceDemo(false)}>
          <div className="voice-modal-premium" onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div className="voice-modal-header-premium">
              <div className="header-left">
                <div className="voice-indicator-dot"></div>
                <h2>Voice Banking Assistant</h2>
              </div>
              <button className="btn-close-premium" onClick={() => setShowVoiceDemo(false)}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </button>
            </div>

            {/* Instructions Banner */}
            {conversation.length === 0 && !isRecording && !isProcessing && !isSpeaking && (
              <div className="welcome-banner">
                <h3>Click the microphone below to start</h3>
                <p className="welcome-subtext">Try: "What's my balance?" or "Send 1000 to John"</p>
              </div>
            )}

            {/* Conversation Area */}
            <div className="conversation-area">
              {conversation.length > 0 ? (
                <div className="messages-container">
                  {conversation.map((msg, idx) => (
                    <div key={idx} className={`message-bubble ${msg.type}`}>
                      <div className="message-avatar-premium">
                        {msg.type === 'user' ? (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                          </svg>
                        ) : (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                          </svg>
                        )}
                      </div>
                      <div className="message-content-premium">
                        <div className="message-text">{msg.text}</div>
                        {msg.intent && <span className="intent-tag">{msg.intent}</span>}
                      </div>
                    </div>
                  ))}
                  {/* Auto-scroll target */}
                  <div ref={conversationEndRef} />
                </div>
              ) : (
                <div className="empty-state">
                  <p>Your conversation will appear here</p>
                </div>
              )}
            </div>

            {/* Controls Area */}
            <div className="controls-area">
              {/* Status Text */}
              <div className="status-text-premium">
                {isSpeaking ? (
                  <>
                    <div className="speaking-indicator"></div>
                    <span className="status-label">Assistant speaking... Click to interrupt</span>
                  </>
                ) : isRecording ? (
                  <>
                    <div className="recording-indicator"></div>
                    <span className="status-label">Listening... Click to stop</span>
                  </>
                ) : isProcessing ? (
                  <>
                    <div className="processing-spinner"></div>
                    <span className="status-label">Preparing to record... (2 seconds)</span>
                  </>
                ) : (
                  <span className="status-label-idle">Click microphone to start speaking</span>
                )}
              </div>

              {/* Mic Button */}
              <button
                className={`mic-button-premium ${isRecording ? 'recording' : ''} ${isProcessing ? 'processing' : ''}`}
                onClick={handleVoiceClick}
                disabled={isProcessing}
                title={isRecording ? 'Click to stop' : 'Click to speak'}
              >
                {isRecording && (
                  <>
                    <span className="pulse-ring-1"></span>
                    <span className="pulse-ring-2"></span>
                    <span className="pulse-ring-3"></span>
                  </>
                )}
                <svg className="mic-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                  <line x1="12" y1="19" x2="12" y2="23"/>
                  <line x1="8" y1="23" x2="16" y2="23"/>
                </svg>
              </button>

              {/* Helper Text */}
              <div className="helper-text-premium">
                {!isRecording && !isProcessing && conversation.length === 0 && (
                  <p>Powered by EchoBank AI • OpenAI Whisper & GPT</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Hidden Audio Element */}
      <audio ref={audioRef} style={{ display: 'none' }} />
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/signup" element={<CompanySignup />} />
        <Route path="/register" element={<CompanySignup />} />
        <Route path="/login" element={<CompanyLogin />} />
        <Route path="/company/:companyId/configure" element={<ConfigureEndpoints />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
