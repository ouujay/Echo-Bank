import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { accountsAPI, recipientsAPI, transfersAPI } from '../services/api';

interface Account {
  id: number;
  account_number: string;
  balance: string;
}

interface Recipient {
  id: number;
  recipient_name: string;
  account_number: string;
  bank_name: string;
  bank_code: string;
  is_favorite: boolean;
}

const Transfer = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [step, setStep] = useState<'select' | 'amount' | 'pin' | 'confirm' | 'success'>(
    'select'
  );
  const [account, setAccount] = useState<Account | null>(null);
  const [recipients, setRecipients] = useState<Recipient[]>([]);
  const [selectedRecipient, setSelectedRecipient] = useState<Recipient | null>(null);
  const [amount, setAmount] = useState('');
  const [narration, setNarration] = useState('');
  const [pin, setPin] = useState(['', '', '', '']);
  const [transactionId, setTransactionId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const accountsData = await accountsAPI.getAccounts();
      if (accountsData && accountsData.length > 0) {
        setAccount(accountsData[0]);
      }

      const recipientsData = await recipientsAPI.getRecipients();
      setRecipients(recipientsData || []);
    } catch (err) {
      setError('Failed to load data');
    }
  };

  const handleSelectRecipient = (recipient: Recipient) => {
    setSelectedRecipient(recipient);
    setStep('amount');
  };

  const handleAmountSubmit = async () => {
    if (!account || !selectedRecipient) return;

    const amountNum = parseFloat(amount);
    if (isNaN(amountNum) || amountNum <= 0) {
      setError('Invalid amount');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await transfersAPI.initiate({
        account_number: account.account_number,
        recipient_id: selectedRecipient.id,
        amount: amountNum,
        narration,
        initiated_via: 'web',
      });

      setTransactionId(response.transaction_id);
      setStep('pin');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to initiate transfer');
    } finally {
      setLoading(false);
    }
  };

  const handlePinChange = (index: number, value: string) => {
    if (value.length > 1) value = value[0];
    if (!/^\d*$/.test(value)) return;

    const newPin = [...pin];
    newPin[index] = value;
    setPin(newPin);

    // Auto-focus next input
    if (value && index < 3) {
      const nextInput = document.getElementById(`pin-${index + 1}`);
      nextInput?.focus();
    }
  };

  const handlePinSubmit = async () => {
    if (!transactionId || !account) return;

    const pinValue = pin.join('');
    if (pinValue.length !== 4) {
      setError('PIN must be 4 digits');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await transfersAPI.verifyPIN(transactionId, pinValue);
      setStep('confirm');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid PIN');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!transactionId) return;

    setLoading(true);
    setError('');

    try {
      const response = await transfersAPI.confirm(transactionId);
      setSuccess(response.message);
      setStep('success');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Transfer failed');
    } finally {
      setLoading(false);
    }
  };

  const handleNewTransfer = () => {
    setStep('select');
    setSelectedRecipient(null);
    setAmount('');
    setNarration('');
    setPin(['', '', '', '']);
    setTransactionId(null);
    setError('');
    setSuccess('');
  };

  const formatCurrency = (value: string) => {
    return `₦${parseFloat(value).toLocaleString('en-NG', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  return (
    <div className="dashboard">
      <div className="navbar">
        <div className="navbar-content">
          <h1>💳 Demo Bank</h1>
          <div className="navbar-links">
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/transfer">Transfer</Link>
            <Link to="/recipients">Recipients</Link>
            <button onClick={() => { logout(); navigate('/login'); }}>Logout</button>
          </div>
        </div>
      </div>

      <div className="transfer-container">
        <h2 style={{ marginBottom: '30px', color: '#333' }}>Send Money</h2>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        {step === 'select' && (
          <div className="card">
            <h3>Select Recipient</h3>
            {recipients.length === 0 ? (
              <div className="empty-state">
                <div className="icon">👥</div>
                <p>No recipients yet</p>
                <Link to="/recipients" className="btn btn-primary" style={{ marginTop: '20px' }}>
                  Add Recipient
                </Link>
              </div>
            ) : (
              <>
                {recipients.map((recipient) => (
                  <div
                    key={recipient.id}
                    className="recipient-card"
                    onClick={() => handleSelectRecipient(recipient)}
                  >
                    <div className="recipient-info">
                      <h4>{recipient.recipient_name}</h4>
                      <p>
                        {recipient.account_number} • {recipient.bank_name}
                      </p>
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>
        )}

        {step === 'amount' && selectedRecipient && (
          <div className="card">
            <h3>Transfer to {selectedRecipient.recipient_name}</h3>
            <p style={{ color: '#999', marginBottom: '20px' }}>
              {selectedRecipient.account_number} • {selectedRecipient.bank_name}
            </p>

            <div className="form-group">
              <label>Amount (₦)</label>
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="0.00"
                min="1"
                step="0.01"
              />
            </div>

            <div className="form-group">
              <label>Narration (Optional)</label>
              <input
                type="text"
                value={narration}
                onChange={(e) => setNarration(e.target.value)}
                placeholder="Payment for..."
                maxLength={100}
              />
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => setStep('select')}
                className="btn btn-secondary"
              >
                Back
              </button>
              <button
                onClick={handleAmountSubmit}
                className="btn btn-primary"
                disabled={loading || !amount}
              >
                {loading ? 'Processing...' : 'Continue'}
              </button>
            </div>
          </div>
        )}

        {step === 'pin' && (
          <div className="card">
            <h3>Enter Your PIN</h3>
            <p style={{ color: '#999', marginBottom: '24px' }}>
              Enter your 4-digit transaction PIN to authorize this transfer
            </p>

            <div className="pin-input">
              {[0, 1, 2, 3].map((index) => (
                <input
                  key={index}
                  id={`pin-${index}`}
                  type="password"
                  maxLength={1}
                  value={pin[index]}
                  onChange={(e) => handlePinChange(index, e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Backspace' && !pin[index] && index > 0) {
                      const prevInput = document.getElementById(`pin-${index - 1}`);
                      prevInput?.focus();
                    }
                  }}
                />
              ))}
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button onClick={() => setStep('amount')} className="btn btn-secondary">
                Back
              </button>
              <button
                onClick={handlePinSubmit}
                className="btn btn-primary"
                disabled={loading || pin.some((d) => !d)}
              >
                {loading ? 'Verifying...' : 'Verify PIN'}
              </button>
            </div>
          </div>
        )}

        {step === 'confirm' && selectedRecipient && (
          <div className="card">
            <h3>Confirm Transfer</h3>
            <div style={{ marginBottom: '24px' }}>
              <div style={{ marginBottom: '16px' }}>
                <p style={{ color: '#999', fontSize: '14px' }}>Recipient</p>
                <h4 style={{ color: '#333' }}>{selectedRecipient.recipient_name}</h4>
                <p style={{ color: '#666' }}>
                  {selectedRecipient.account_number} • {selectedRecipient.bank_name}
                </p>
              </div>
              <div style={{ marginBottom: '16px' }}>
                <p style={{ color: '#999', fontSize: '14px' }}>Amount</p>
                <h2 style={{ color: '#667eea', margin: '8px 0' }}>
                  {formatCurrency(amount)}
                </h2>
              </div>
              {narration && (
                <div>
                  <p style={{ color: '#999', fontSize: '14px' }}>Narration</p>
                  <p style={{ color: '#666' }}>{narration}</p>
                </div>
              )}
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button onClick={() => setStep('pin')} className="btn btn-secondary">
                Cancel
              </button>
              <button
                onClick={handleConfirm}
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? 'Processing...' : 'Confirm Transfer'}
              </button>
            </div>
          </div>
        )}

        {step === 'success' && (
          <div className="card" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '64px', marginBottom: '16px' }}>✅</div>
            <h2 style={{ color: '#22c55e', marginBottom: '12px' }}>Transfer Successful!</h2>
            <p style={{ color: '#666', marginBottom: '24px' }}>
              Your transfer of {formatCurrency(amount)} to {selectedRecipient?.recipient_name} was successful
            </p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button onClick={handleNewTransfer} className="btn btn-secondary">
                New Transfer
              </button>
              <button
                onClick={() => navigate('/dashboard')}
                className="btn btn-primary"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Transfer;
