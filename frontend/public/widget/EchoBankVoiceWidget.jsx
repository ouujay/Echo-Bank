/**
 * EchoBank Voice Widget
 *
 * Drop-in voice banking component for any React application
 *
 * Usage:
 *
 * import EchoBankVoiceWidget from './EchoBankVoiceWidget';
 * import './EchoBankVoiceWidget.css';
 *
 * function App() {
 *   const [showVoice, setShowVoice] = useState(false);
 *
 *   return (
 *     <>
 *       <button onClick={() => setShowVoice(true)}>🎤 Voice Banking</button>
 *
 *       {showVoice && (
 *         <EchoBankVoiceWidget
 *           companyId="YOUR_COMPANY_ID"
 *           accountNumber={user.accountNumber}
 *           userToken={user.token}
 *           onClose={() => setShowVoice(false)}
 *           echoBankApiUrl="http://localhost:8000"  // Optional, defaults to this
 *         />
 *       )}
 *     </>
 *   );
 * }
 */

import { useState, useRef, useEffect } from 'react';

const EchoBankVoiceWidget = ({
  companyId,
  accountNumber,
  userToken,
  onClose,
  echoBankApiUrl = 'http://localhost:8000'
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [conversation, setConversation] = useState([]);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null);
  const recordingDelayTimeoutRef = useRef(null);
  const currentSessionId = useRef(`session_${accountNumber}_${Date.now()}`);

  useEffect(() => {
    // Create audio element
    audioRef.current = new Audio();

    // Cleanup
    return () => {
      if (recordingDelayTimeoutRef.current) {
        clearTimeout(recordingDelayTimeoutRef.current);
      }
      stopRecording();
    };
  }, []);

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsSpeaking(false);
    }
  };

  const playAudioResponse = (base64Audio) => {
    const audioData = `data:audio/mp3;base64,${base64Audio}`;
    if (audioRef.current) {
      audioRef.current.src = audioData;
      setIsSpeaking(true);
      audioRef.current.play();

      audioRef.current.onended = () => {
        setIsSpeaking(false);
      };

      audioRef.current.onerror = () => {
        console.error('Error playing audio');
        setIsSpeaking(false);
      };
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await sendAudioToEchoBank(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Please allow microphone access to use voice banking');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const sendAudioToEchoBank = async (audioBlob) => {
    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob);

      const response = await fetch(`${echoBankApiUrl}/api/v1/voice/process-audio?include_audio=true`, {
        method: 'POST',
        headers: {
          'account-number': accountNumber,
          'company-id': String(companyId),
          'session-id': currentSessionId.current,
          'token': userToken,
        },
        body: formData
      });

      const result = await response.json();

      if (result.success) {
        // Add user message
        if (result.data?.transcript) {
          setConversation(prev => [...prev, {
            type: 'user',
            text: result.data.transcript,
            intent: result.intent
          }]);
        }

        // Add assistant response
        setConversation(prev => [...prev, {
          type: 'assistant',
          text: result.response_text
        }]);

        // Play audio response
        if (result.response_audio) {
          playAudioResponse(result.response_audio);
        }
      } else {
        setConversation(prev => [...prev, {
          type: 'assistant',
          text: result.response_text || 'Sorry, something went wrong. Please try again.'
        }]);
      }
    } catch (error) {
      console.error('Error sending audio:', error);
      setConversation(prev => [...prev, {
        type: 'assistant',
        text: 'Failed to connect to voice service. Please try again.'
      }]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleVoiceClick = async () => {
    if (isRecording) {
      stopRecording();
      return;
    }

    if (isSpeaking) {
      stopAudio();
      return;
    }

    if (recordingDelayTimeoutRef.current) {
      clearTimeout(recordingDelayTimeoutRef.current);
    }

    // Wait 2 seconds before recording
    setIsProcessing(true);
    recordingDelayTimeoutRef.current = setTimeout(async () => {
      setIsProcessing(false);
      await startRecording();
    }, 2000);
  };

  return (
    <div className="echobank-modal-overlay" onClick={onClose}>
      <div className="echobank-voice-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="echobank-modal-header">
          <div className="echobank-header-left">
            <div className="echobank-indicator-dot"></div>
            <h2>Voice Banking</h2>
          </div>
          <button className="echobank-btn-close" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Welcome Banner */}
        {conversation.length === 0 && !isRecording && !isProcessing && !isSpeaking && (
          <div className="echobank-welcome-banner">
            <h3>Click the microphone below to start</h3>
            <p className="echobank-welcome-subtext">Try: "What's my balance?" or "Send 1000 to John"</p>
          </div>
        )}

        {/* Conversation Area */}
        <div className="echobank-conversation-area">
          {conversation.length > 0 ? (
            <div className="echobank-messages-container">
              {conversation.map((msg, idx) => (
                <div key={idx} className={`echobank-message-bubble ${msg.type}`}>
                  <div className="echobank-message-avatar">
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
                  <div className="echobank-message-content">
                    <div className="echobank-message-text">{msg.text}</div>
                    {msg.intent && <span className="echobank-intent-tag">{msg.intent}</span>}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="echobank-empty-state">
              <p>Start speaking to interact with voice banking</p>
            </div>
          )}
        </div>

        {/* Controls Area */}
        <div className="echobank-controls-area">
          {/* Status Text */}
          <div className="echobank-status-text">
            {isSpeaking ? (
              <>
                <div className="echobank-speaking-indicator"></div>
                <span className="echobank-status-label">Assistant speaking... Click to interrupt</span>
              </>
            ) : isRecording ? (
              <>
                <div className="echobank-recording-indicator"></div>
                <span className="echobank-status-label">Listening... Click to stop</span>
              </>
            ) : isProcessing ? (
              <>
                <div className="echobank-processing-spinner"></div>
                <span className="echobank-status-label">Preparing to record... (2 seconds)</span>
              </>
            ) : (
              <span className="echobank-status-label-idle">Click microphone to start speaking</span>
            )}
          </div>

          {/* Mic Button */}
          <button
            onClick={handleVoiceClick}
            className={`echobank-mic-button ${isRecording ? 'recording' : ''} ${isProcessing ? 'processing' : ''}`}
            disabled={isProcessing && !isRecording && !isSpeaking}
          >
            {isRecording && (
              <>
                <span className="echobank-pulse-ring-1"></span>
                <span className="echobank-pulse-ring-2"></span>
                <span className="echobank-pulse-ring-3"></span>
              </>
            )}
            <svg className="echobank-mic-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              {isRecording ? (
                <rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor" />
              ) : (
                <>
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                  <line x1="12" y1="19" x2="12" y2="23" />
                  <line x1="8" y1="23" x2="16" y2="23" />
                </>
              )}
            </svg>
          </button>

          {/* Helper Text */}
          <div className="echobank-helper-text">
            {!isRecording && !isProcessing && !isSpeaking && (
              <p>Tap microphone and speak your command</p>
            )}
          </div>
        </div>

        {/* Powered by EchoBank */}
        <div className="echobank-footer">
          <span>Powered by <strong>EchoBank</strong></span>
        </div>
      </div>
    </div>
  );
};

export default EchoBankVoiceWidget;
