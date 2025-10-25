import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { recipientsAPI } from '../services/api';

interface Recipient {
  id: number;
  recipient_name: string;
  account_number: string;
  bank_name: string;
  bank_code: string;
  is_favorite: boolean;
}

const Recipients = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const [recipients, setRecipients] = useState<Recipient[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    recipient_name: '',
    account_number: '',
    bank_name: '',
    bank_code: '',
  });

  useEffect(() => {
    loadRecipients();
  }, []);

  const loadRecipients = async () => {
    try {
      const data = await recipientsAPI.getRecipients();
      setRecipients(data || []);
    } catch (err) {
      setError('Failed to load recipients');
    }
  };

  const handleAddRecipient = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await recipientsAPI.addRecipient(formData);
      setSuccess('Recipient added successfully!');
      setShowAddModal(false);
      setFormData({
        recipient_name: '',
        account_number: '',
        bank_name: '',
        bank_code: '',
      });
      loadRecipients();

      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add recipient');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFavorite = async (id: number) => {
    try {
      await recipientsAPI.toggleFavorite(id);
      loadRecipients();
    } catch (err) {
      setError('Failed to update recipient');
    }
  };

  const handleDeleteRecipient = async (id: number) => {
    if (!confirm('Are you sure you want to delete this recipient?')) return;

    try {
      await recipientsAPI.deleteRecipient(id);
      setSuccess('Recipient deleted');
      loadRecipients();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to delete recipient');
    }
  };

  const banks = [
    { name: 'Demo Bank', code: '999' },
    { name: 'GTBank', code: '058' },
    { name: 'Access Bank', code: '044' },
    { name: 'First Bank', code: '011' },
    { name: 'UBA', code: '033' },
    { name: 'Zenith Bank', code: '057' },
    { name: 'Kuda', code: '090267' },
  ];

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

      <div className="container">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
          <h2 style={{ color: '#333' }}>Saved Recipients</h2>
          <button
            onClick={() => setShowAddModal(true)}
            className="btn btn-primary"
            style={{ width: 'auto', padding: '10px 24px' }}
          >
            + Add Recipient
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        {recipients.length === 0 ? (
          <div className="card">
            <div className="empty-state">
              <div className="icon">👥</div>
              <p>No recipients yet</p>
              <button
                onClick={() => setShowAddModal(true)}
                className="btn btn-primary"
                style={{ marginTop: '20px' }}
              >
                Add Your First Recipient
              </button>
            </div>
          </div>
        ) : (
          <div className="card">
            {recipients.map((recipient) => (
              <div key={recipient.id} className="recipient-card">
                <div className="recipient-info">
                  <h4>
                    {recipient.is_favorite && '⭐ '}
                    {recipient.recipient_name}
                  </h4>
                  <p>
                    {recipient.account_number} • {recipient.bank_name}
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    onClick={() => handleToggleFavorite(recipient.id)}
                    style={{
                      padding: '8px 12px',
                      border: '1px solid #e0e0e0',
                      borderRadius: '6px',
                      background: 'white',
                      cursor: 'pointer',
                    }}
                  >
                    {recipient.is_favorite ? '⭐' : '☆'}
                  </button>
                  <button
                    onClick={() => handleDeleteRecipient(recipient.id)}
                    style={{
                      padding: '8px 12px',
                      border: '1px solid #fee',
                      borderRadius: '6px',
                      background: '#fee',
                      color: '#c33',
                      cursor: 'pointer',
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {showAddModal && (
          <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <h2>Add New Recipient</h2>
              <form onSubmit={handleAddRecipient}>
                <div className="form-group">
                  <label>Recipient Name</label>
                  <input
                    type="text"
                    value={formData.recipient_name}
                    onChange={(e) => setFormData({ ...formData, recipient_name: e.target.value })}
                    placeholder="John Doe"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Account Number</label>
                  <input
                    type="text"
                    value={formData.account_number}
                    onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
                    placeholder="0123456789"
                    required
                    maxLength={10}
                    pattern="\d{10}"
                  />
                </div>

                <div className="form-group">
                  <label>Bank</label>
                  <select
                    value={formData.bank_code}
                    onChange={(e) => {
                      const selected = banks.find((b) => b.code === e.target.value);
                      setFormData({
                        ...formData,
                        bank_code: e.target.value,
                        bank_name: selected?.name || '',
                      });
                    }}
                    required
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '8px',
                      fontSize: '16px',
                    }}
                  >
                    <option value="">Select a bank</option>
                    {banks.map((bank) => (
                      <option key={bank.code} value={bank.code}>
                        {bank.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Adding...' : 'Add Recipient'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Recipients;
