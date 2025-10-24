import api from './api';
import { mockTransferService } from './mockService'; // TODO: Remove before production

// TODO: Remove this function before production
const isDemoMode = () => localStorage.getItem('DEMO_MODE') === 'true';

export const transferService = {
  /**
   * Search for recipients by name
   */
  async searchRecipients(name, limit = 5) {
    // TODO: Remove demo mode check before production
    if (isDemoMode()) return mockTransferService.searchRecipients(name, limit);

    const response = await api.get('/api/v1/recipients/search', {
      params: { name, limit },
    });
    return response.data;
  },

  /**
   * Initiate a new transfer
   */
  async initiateTransfer(recipientId, amount, sessionId) {
    // TODO: Remove demo mode check before production
    if (isDemoMode()) return mockTransferService.initiateTransfer(recipientId, amount, sessionId);

    const response = await api.post('/api/v1/transfers/initiate', {
      recipient_id: recipientId,
      amount,
      session_id: sessionId,
    });
    return response.data;
  },

  /**
   * Verify PIN for transfer
   */
  async verifyPin(transferId, pin) {
    // TODO: Remove demo mode check before production
    if (isDemoMode()) return mockTransferService.verifyPin(transferId, pin);

    const response = await api.post(
      `/api/v1/transfers/${transferId}/verify-pin`,
      { pin }
    );
    return response.data;
  },

  /**
   * Confirm transfer
   */
  async confirmTransfer(transferId) {
    // TODO: Remove demo mode check before production
    if (isDemoMode()) return mockTransferService.confirmTransfer(transferId);

    const response = await api.post(
      `/api/v1/transfers/${transferId}/confirm`,
      { confirmation: 'confirm' }
    );
    return response.data;
  },

  /**
   * Cancel transfer
   */
  async cancelTransfer(transferId) {
    // TODO: Remove demo mode check before production
    if (isDemoMode()) return mockTransferService.cancelTransfer(transferId);

    const response = await api.post(`/api/v1/transfers/${transferId}/cancel`);
    return response.data;
  },
};
