import api from './api';
import { mockVoiceService } from './mockService'; // TODO: Remove before production

// TODO: Remove this function before production
const isDemoMode = () => localStorage.getItem('DEMO_MODE') === 'true';

export const voiceService = {
  /**
   * Transcribe audio file to text
   */
  async transcribeAudio(audioBlob, sessionId = null) {
    // TODO: Remove demo mode check before production
    if (isDemoMode()) return mockVoiceService.transcribeAudio(audioBlob, sessionId);

    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    if (sessionId) {
      formData.append('session_id', sessionId);
    }

    const response = await api.post('/api/v1/voice/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  /**
   * Parse intent from transcript
   */
  async parseIntent(transcript, sessionId) {
    // TODO: Remove demo mode check before production
    if (isDemoMode()) return mockVoiceService.parseIntent(transcript, sessionId);

    const response = await api.post('/api/v1/voice/intent', {
      transcript,
      session_id: sessionId,
    });

    return response.data;
  },

  /**
   * Get session state
   */
  async getSession(sessionId) {
    // TODO: Remove demo mode check before production
    if (isDemoMode()) return mockVoiceService.getSession(sessionId);

    const response = await api.get(`/api/v1/voice/session/${sessionId}`);
    return response.data;
  },
};
