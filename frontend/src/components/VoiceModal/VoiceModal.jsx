import { useState, useEffect, useRef } from 'react';
import { useVoice } from '../../hooks/useVoice';
import { voiceService } from '../../services/voiceService';
import styles from './VoiceModal.module.css';

export const VoiceModal = ({ onClose, onTranscript }) => {
  const { isRecording, isProcessing, transcript, startRecording, stopRecording } = useVoice();
  const [sessionId] = useState(`sess_${Math.random().toString(36).substr(2, 9)}`);
  const hasStarted = useRef(false);

  // Auto-start recording when modal opens
  useEffect(() => {
    const initRecording = async () => {
      if (!hasStarted.current) {
        hasStarted.current = true;
        await startRecording();

        // Auto-stop after 5 seconds
        setTimeout(() => {
          stopRecording();
        }, 5000);
      }
    };

    initRecording();
  }, [startRecording, stopRecording]);

  const handleTranscriptComplete = async () => {
    if (transcript) {
      // Parse intent
      const intentResponse = await voiceService.parseIntent(transcript, sessionId);
      onTranscript(transcript, intentResponse.data);
    }
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h2>Voice Assistant</h2>
          <button className={styles.closeBtn} onClick={onClose}>×</button>
        </div>

        <div className={styles.content}>
          <div
            className={`${styles.voiceButton} ${isRecording ? styles.recording : ''} ${isProcessing ? styles.processing : ''}`}
          >
            <div className={styles.voiceButtonInner}>
              {isProcessing ? (
                <div className={styles.spinner}></div>
              ) : (
                <>
                  <span className={styles.micIcon}>🎤</span>
                  {isRecording && (
                    <div className={styles.pulseRings}>
                      <div className={styles.pulseRing}></div>
                      <div className={styles.pulseRing}></div>
                      <div className={styles.pulseRing}></div>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>

          <p className={styles.hint}>
            {isRecording ? 'Listening...' : isProcessing ? 'Processing...' : 'Starting...'}
          </p>

          {transcript && (
            <div className={styles.transcript}>
              <p className={styles.transcriptLabel}>You said:</p>
              <p className={styles.transcriptText}>{transcript}</p>
              <button className={styles.confirmBtn} onClick={handleTranscriptComplete}>
                Continue
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
