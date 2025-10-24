import { useState } from 'react'
import './App.css'
import { VoiceModal } from './components/VoiceModal/VoiceModal'
import { Transcript } from './components/Transcript/Transcript'
import { PinModal, ConfirmModal } from './components/TransferFlow'
import { DemoToggle } from './components/DemoToggle' // TODO: Remove before production
import { useTransfer } from './hooks/useTransfer'

function App() {
  const [conversation, setConversation] = useState([])
  const [showVoiceModal, setShowVoiceModal] = useState(false)
  const [showPinModal, setShowPinModal] = useState(false)
  const [showConfirmModal, setShowConfirmModal] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [transferSuccess, setTransferSuccess] = useState(false)

  const {
    isLoading,
    error,
    currentTransfer,
    transferStatus,
    searchRecipient,
    initiateTransfer,
    verifyPin,
    confirmTransfer,
    cancelTransfer,
    resetTransfer
  } = useTransfer()

  // Handle voice modal open
  const handleVoiceClick = () => {
    setShowVoiceModal(true)
  }

  // Handle transcript from voice modal
  const handleTranscript = async (transcript, intent) => {
    console.log('Transcript:', transcript)
    console.log('Intent:', intent)

    // Add user message to conversation
    setConversation(prev => [
      ...prev,
      { type: 'user', text: transcript, timestamp: new Date().toISOString() }
    ])

    setShowVoiceModal(false)

    // Handle different intents
    if (intent.intent === 'transfer') {
      await handleTransferIntent(intent, transcript)
    } else if (intent.intent === 'check_balance') {
      addBotMessage('Your current balance is ₦45,320. How can I help you today?')
    } else if (intent.intent === 'cancel') {
      if (currentTransfer) {
        await handleCancelTransfer()
      } else {
        addBotMessage('There is no active transfer to cancel.')
      }
    } else {
      addBotMessage(`I understood: ${intent.intent}. This feature is coming soon!`)
    }
  }

  // Handle transfer intent
  const handleTransferIntent = async (intent, transcript) => {
    try {
      const { entities } = intent
      const recipientName = entities.recipient
      const amount = entities.amount

      if (!recipientName || !amount) {
        addBotMessage('I need both a recipient name and amount. Please try again.')
        return
      }

      // Search for recipient
      addBotMessage(`Searching for ${recipientName}...`)

      try {
        const searchResult = await searchRecipient(recipientName)

        if (searchResult.match_type === 'single') {
          const recipient = searchResult.recipients[0]
          addBotMessage(`Found ${recipient.name} at ${recipient.bank_name}.`)

          // Initiate transfer
          const newSessionId = `sess_${Math.random().toString(36).substr(2, 9)}`
          setSessionId(newSessionId)

          const transferData = await initiateTransfer(recipient.id, amount, newSessionId)
          addBotMessage(transferData.message)

          // Show PIN modal
          setShowPinModal(true)
        } else if (searchResult.match_type === 'multiple') {
          addBotMessage(searchResult.message)
          // TODO: Handle multiple recipients selection
        }
      } catch (err) {
        const errorMsg = err.response?.data?.error?.message || 'Failed to process transfer'
        addBotMessage(`Error: ${errorMsg}`)
      }
    } catch (err) {
      addBotMessage('Sorry, I had trouble processing that. Please try again.')
    }
  }

  // Handle PIN verification
  const handlePinVerify = async (pin) => {
    try {
      await verifyPin(currentTransfer.transfer_id, pin)
      addBotMessage('PIN verified successfully.')
      setShowPinModal(false)
      setShowConfirmModal(true)
    } catch (err) {
      // Error is already set in useTransfer hook
      console.error('PIN verification failed:', err)
    }
  }

  // Handle transfer confirmation
  const handleConfirm = async () => {
    try {
      const result = await confirmTransfer(currentTransfer.transfer_id)
      addBotMessage(result.data.message)
      setTransferSuccess(true)
    } catch (err) {
      const errorMsg = err.response?.data?.error?.message || 'Transfer failed'
      addBotMessage(`Error: ${errorMsg}`)
      setShowConfirmModal(false)
    }
  }

  // Handle transfer cancellation
  const handleCancelTransfer = async () => {
    try {
      if (currentTransfer) {
        await cancelTransfer(currentTransfer.transfer_id)
        addBotMessage('Transfer cancelled. No money was sent.')
        setShowPinModal(false)
        setShowConfirmModal(false)
      }
    } catch (err) {
      addBotMessage('Failed to cancel transfer.')
    }
  }

  // Close confirm modal
  const handleCloseConfirmModal = () => {
    setShowConfirmModal(false)
    setTransferSuccess(false)
    resetTransfer()
  }

  // Add bot message to conversation
  const addBotMessage = (text) => {
    setConversation(prev => [
      ...prev,
      { type: 'bot', text, timestamp: new Date().toISOString() }
    ])
  }

  // Clear conversation
  const handleClearConversation = () => {
    setConversation([])
    resetTransfer()
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
                className="voice-button"
                onClick={handleVoiceClick}
              >
                <div className="voice-button-inner">
                  <div className="mic-icon">🎤</div>
                </div>
              </button>
              <p className="voice-hint">
                Tap to speak
              </p>
            </div>

            {/* Conversation Display */}
            <Transcript
              messages={conversation}
              onClear={handleClearConversation}
            />
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

      {/* Modals */}
      {showVoiceModal && (
        <VoiceModal
          onClose={() => setShowVoiceModal(false)}
          onTranscript={handleTranscript}
        />
      )}

      {showPinModal && currentTransfer && (
        <PinModal
          onClose={() => {
            setShowPinModal(false)
            handleCancelTransfer()
          }}
          onVerify={handlePinVerify}
          transferData={currentTransfer}
          isLoading={isLoading}
          error={error}
        />
      )}

      {showConfirmModal && currentTransfer && (
        <ConfirmModal
          onClose={handleCloseConfirmModal}
          onConfirm={handleConfirm}
          transferData={currentTransfer}
          isLoading={isLoading}
          isSuccess={transferSuccess}
        />
      )}

      {/* TODO: Remove DemoToggle before production */}
      <DemoToggle />
    </div>
  )
}

export default App
