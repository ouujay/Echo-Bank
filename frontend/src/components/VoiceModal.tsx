import { useState, useRef, useEffect } from 'react';
import './VoiceModal.css';

interface VoiceModalProps {
  accountNumber: string;
  userToken: string;
  onClose: () => void;
}

interface Message {
  type: 'user' | 'assistant';
  text: string;
  intent?: string;
}

const VoiceModal = ({ accountNumber, userToken, onClose }: VoiceModalProps) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [conversation, setConversation] = useState<Message[]>([]);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const recordingDelayTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const currentSessionId = useRef(`session_${accountNumber}_${Date.now()}`);

  const ECHOBANK_API = 'http://localhost:8000';
  const COMPANY_ID = '4'; // Demo Bank's company ID (registered in EchoBank)

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

  const playAudioResponse = (base64Audio: string) => {
    // Support both WAV (pyttsx3) and MP3 (OpenAI TTS)
    const audioData = `data:audio/wav;base64,${base64Audio}`;
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

  const sendAudioToEchoBank = async (audioBlob: Blob) => {
    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob);

      const response = await fetch(`${ECHOBANK_API}/api/v1/voice/process-audio`, {
        method: 'POST',
        headers: {
          'account-number': accountNumber,
          'company-id': COMPANY_ID,
          'session-id': currentSessionId.current,
          'token': userToken,
          'include-audio': 'true',  // Request TTS audio response
        },
        body: formData
      });

      const result = await response.json();

      console.log('[DEBUG] EchoBank Response:', result);

      if (result.success) {
        // Add user message (transcript might be directly in result or in result.data)
        const transcript = result.transcript || result.data?.transcript;
        if (transcript) {
          setConversation(prev => [...prev, {
            type: 'user',
            text: transcript,
            intent: result.intent
          }]);
        }

        // Add assistant response
        setConversation(prev => [...prev, {
          type: 'assistant',
          text: result.response_text
        }]);

        // Play audio response (field name is response_audio, not audio_base64)
        if (result.response_audio) {
          console.log('[DEBUG] Playing TTS audio response...');
          playAudioResponse(result.response_audio);
        } else {
          console.warn('[WARNING] No response_audio in result. TTS not enabled.');
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

    // Stop audio if playing
    if (isSpeaking) {
      stopAudio();
      return;
    }

    // Clear existing timeout
    if (recordingDelayTimeoutRef.current) {
      clearTimeout(recordingDelayTimeoutRef.current);
    }

    // Start recording immediately (removed 2-second delay)
    await startRecording();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="voice-modal-premium" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="voice-modal-header-premium">
          <div className="header-left">
            <div className="voice-indicator-dot"></div>
            <h2>Voice Banking Assistant</h2>
          </div>
          <button className="btn-close-premium" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Welcome Banner */}
        {conversation.length === 0 && !isRecording && !isProcessing && !isSpeaking && (
          <div className="welcome-banner">
            <div className="welcome-icon">🎙️</div>
            <h3>Welcome to Voice Banking</h3>
            <p className="welcome-subtext">Click the microphone and try saying:</p>
            <p className="welcome-subtext">"Check my balance" • "Show my recipients" • "View transactions"</p>
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
            </div>
          ) : (
            <div className="empty-state">
              <p>Start speaking to interact with voice banking</p>
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
            onClick={handleVoiceClick}
            className={`mic-button-premium ${isRecording ? 'recording' : ''} ${isProcessing ? 'processing' : ''}`}
            disabled={isProcessing && !isRecording && !isSpeaking}
          >
            {isRecording && (
              <>
                <span className="pulse-ring-1"></span>
                <span className="pulse-ring-2"></span>
                <span className="pulse-ring-3"></span>
              </>
            )}
            <svg className="mic-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
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
          <div className="helper-text-premium">
            {!isRecording && !isProcessing && !isSpeaking && (
              <p>Tap microphone and speak your command</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceModal;
