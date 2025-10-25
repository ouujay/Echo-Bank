import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { accountsAPI } from '../services/api';

interface Account {
  id: number;
  account_number: string;
  account_name: string;
  balance: string;
  currency: string;
}

interface Transaction {
  id: number;
  transaction_ref: string;
  transaction_type: string;
  amount: string;
  recipient_name?: string;
  status: string;
  created_at: string;
}

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [account, setAccount] = useState<Account | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      // Get accounts
      const accountsData = await accountsAPI.getAccounts();
      if (accountsData && accountsData.length > 0) {
        setAccount(accountsData[0]);

        // Get transactions
        const txnsData = await accountsAPI.getTransactions(accountsData[0].id);
        setTransactions(txnsData.transactions || []);
      }
    } catch (err: any) {
      setError('Failed to load data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const formatCurrency = (amount: string) => {
    return `₦${parseFloat(amount).toLocaleString('en-NG', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="navbar">
          <div className="navbar-content">
            <h1>💳 Demo Bank</h1>
          </div>
        </div>
        <div className="container">
          <div className="loading">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="navbar">
        <div className="navbar-content">
          <h1>💳 Demo Bank</h1>
          <div className="navbar-links">
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/transfer">Transfer</Link>
            <Link to="/recipients">Recipients</Link>
            <button onClick={handleLogout}>Logout</button>
          </div>
        </div>
      </div>

      <div className="container">
        <h2 style={{ marginBottom: '20px', color: '#333' }}>
          Welcome back, {user?.full_name}!
        </h2>

        {error && <div className="error-message">{error}</div>}

        {account && (
          <div className="balance-card">
            <h2>Available Balance</h2>
            <div className="amount">{formatCurrency(account.balance)}</div>
            <div className="account-number">
              Account: {account.account_number} • {account.account_name}
            </div>
          </div>
        )}

        <div className="quick-actions">
          <Link to="/transfer" className="action-card">
            <div className="icon">💸</div>
            <h4>Send Money</h4>
            <p>Transfer to saved recipients</p>
          </Link>
          <Link to="/recipients" className="action-card">
            <div className="icon">👥</div>
            <h4>Recipients</h4>
            <p>Manage your beneficiaries</p>
          </Link>
          <div className="action-card" onClick={loadData} style={{ cursor: 'pointer' }}>
            <div className="icon">🔄</div>
            <h4>Refresh</h4>
            <p>Update your balance</p>
          </div>
        </div>

        <div className="card">
          <h3>Recent Transactions</h3>
          {transactions.length === 0 ? (
            <div className="empty-state">
              <div className="icon">📭</div>
              <p>No transactions yet</p>
            </div>
          ) : (
            <ul className="transaction-list">
              {transactions.slice(0, 10).map((txn) => (
                <li key={txn.id} className="transaction-item">
                  <div className="transaction-details">
                    <h4>
                      {txn.transaction_type === 'transfer'
                        ? `Transfer to ${txn.recipient_name || 'Recipient'}`
                        : txn.transaction_type === 'credit'
                        ? 'Credit'
                        : 'Debit'}
                    </h4>
                    <p>
                      {formatDate(txn.created_at)} • {txn.transaction_ref}
                    </p>
                    <span className={`status-badge ${txn.status}`}>
                      {txn.status}
                    </span>
                  </div>
                  <div
                    className={`transaction-amount ${
                      txn.transaction_type === 'credit' ? 'credit' : 'debit'
                    }`}
                  >
                    {txn.transaction_type === 'credit' ? '+' : '-'}
                    {formatCurrency(txn.amount)}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
