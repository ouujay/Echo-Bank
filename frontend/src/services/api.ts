import axios from 'axios';

const API_BASE_URL = 'http://localhost:8002/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;

// Auth API
export const authAPI = {
  register: async (data: {
    email: string;
    phone: string;
    full_name: string;
    password: string;
    pin: string;
  }) => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  verifyPIN: async (account_number: string, pin: string) => {
    const response = await api.post('/auth/verify-pin', {
      account_number,
      pin,
    });
    return response.data;
  },
};

// Accounts API
export const accountsAPI = {
  getAccounts: async () => {
    const response = await api.get('/accounts');
    return response.data;
  },

  getBalance: async (accountNumber: string) => {
    const response = await api.get(`/accounts/balance/${accountNumber}`);
    return response.data;
  },

  getTransactions: async (accountId: number, page = 1, pageSize = 20) => {
    const response = await api.get(`/accounts/${accountId}/transactions`, {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },
};

// Recipients API
export const recipientsAPI = {
  getRecipients: async () => {
    const response = await api.get('/recipients');
    return response.data;
  },

  addRecipient: async (data: {
    recipient_name: string;
    account_number: string;
    bank_name: string;
    bank_code: string;
    is_favorite?: boolean;
  }) => {
    const response = await api.post('/recipients', data);
    return response.data;
  },

  toggleFavorite: async (recipientId: number) => {
    const response = await api.put(`/recipients/${recipientId}/favorite`);
    return response.data;
  },

  deleteRecipient: async (recipientId: number) => {
    const response = await api.delete(`/recipients/${recipientId}`);
    return response.data;
  },
};

// Transfers API
export const transfersAPI = {
  initiate: async (data: {
    account_number: string;
    recipient_id?: number;
    recipient_account?: string;
    recipient_name?: string;
    recipient_bank_code?: string;
    recipient_bank_name?: string;
    amount: number;
    narration?: string;
    initiated_via?: string;
  }) => {
    const response = await api.post('/transfers/initiate', data);
    return response.data;
  },

  verifyPIN: async (transactionId: number, pin: string) => {
    const response = await api.post(`/transfers/${transactionId}/verify-pin`, {
      transaction_id: transactionId,
      pin,
    });
    return response.data;
  },

  confirm: async (transactionId: number) => {
    const response = await api.post(`/transfers/${transactionId}/confirm`, {
      transaction_id: transactionId,
    });
    return response.data;
  },

  getStatus: async (transactionId: number) => {
    const response = await api.get(`/transfers/${transactionId}`);
    return response.data;
  },

  cancel: async (transactionId: number) => {
    const response = await api.post(`/transfers/${transactionId}/cancel`);
    return response.data;
  },
};
