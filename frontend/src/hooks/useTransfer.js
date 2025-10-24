import { useState } from 'react';
import { transferService } from '../services/transferService';

export const useTransfer = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentTransfer, setCurrentTransfer] = useState(null);
  const [transferStatus, setTransferStatus] = useState('idle'); // idle, initiated, pin_verified, completed, failed

  const searchRecipient = async (name) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await transferService.searchRecipients(name);
      setIsLoading(false);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to search recipient');
      setIsLoading(false);
      throw err;
    }
  };

  const initiateTransfer = async (recipientId, amount, sessionId) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await transferService.initiateTransfer(recipientId, amount, sessionId);
      setCurrentTransfer(response.data);
      setTransferStatus('initiated');
      setIsLoading(false);
      return response.data;
    } catch (err) {
      const errorData = err.response?.data?.error;
      setError(errorData?.message || 'Failed to initiate transfer');
      setIsLoading(false);
      throw err;
    }
  };

  const verifyPin = async (transferId, pin) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await transferService.verifyPin(transferId, pin);
      setTransferStatus('pin_verified');
      setIsLoading(false);
      return response.data;
    } catch (err) {
      const errorData = err.response?.data?.error;
      setError(errorData?.message || 'Failed to verify PIN');
      setIsLoading(false);
      throw err;
    }
  };

  const confirmTransfer = async (transferId) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await transferService.confirmTransfer(transferId);
      setTransferStatus('completed');
      setIsLoading(false);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to confirm transfer');
      setTransferStatus('failed');
      setIsLoading(false);
      throw err;
    }
  };

  const cancelTransfer = async (transferId) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await transferService.cancelTransfer(transferId);
      setTransferStatus('idle');
      setCurrentTransfer(null);
      setIsLoading(false);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to cancel transfer');
      setIsLoading(false);
      throw err;
    }
  };

  const resetTransfer = () => {
    setCurrentTransfer(null);
    setTransferStatus('idle');
    setError(null);
  };

  return {
    isLoading,
    error,
    currentTransfer,
    transferStatus,
    searchRecipient,
    initiateTransfer,
    verifyPin,
    confirmTransfer,
    cancelTransfer,
    resetTransfer,
  };
};
