import { useState } from 'react';
import styles from './PinModal.module.css';

export const PinModal = ({ onClose, onVerify, transferData, isLoading, error }) => {
  const [pin, setPin] = useState('');
  const [showPin, setShowPin] = useState(false);

  const handlePinChange = (e) => {
    const value = e.target.value.replace(/\D/g, ''); // Only digits
    if (value.length <= 4) {
      setPin(value);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (pin.length === 4) {
      onVerify(pin);
    }
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h2>Verify PIN</h2>
          <button className={styles.closeBtn} onClick={onClose}>×</button>
        </div>

        <div className={styles.content}>
          {/* Transfer Summary */}
          {transferData && (
            <div className={styles.summary}>
              <div className={styles.summaryRow}>
                <span className={styles.label}>Recipient:</span>
                <span className={styles.value}>{transferData.recipient?.name}</span>
              </div>
              <div className={styles.summaryRow}>
                <span className={styles.label}>Amount:</span>
                <span className={styles.amount}>₦{transferData.amount?.toLocaleString()}</span>
              </div>
              <div className={styles.summaryRow}>
                <span className={styles.label}>New Balance:</span>
                <span className={styles.value}>₦{transferData.new_balance?.toLocaleString()}</span>
              </div>
            </div>
          )}

          {/* PIN Input */}
          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.pinInputContainer}>
              <label className={styles.inputLabel}>Enter your 4-digit PIN</label>
              <div className={styles.pinInputWrapper}>
                <input
                  type={showPin ? 'text' : 'password'}
                  value={pin}
                  onChange={handlePinChange}
                  className={styles.pinInput}
                  placeholder="••••"
                  maxLength={4}
                  autoFocus
                  disabled={isLoading}
                />
                <button
                  type="button"
                  className={styles.toggleBtn}
                  onClick={() => setShowPin(!showPin)}
                >
                  {showPin ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
              {error && (
                <div className={styles.error}>
                  ⚠️ {error}
                </div>
              )}
            </div>

            <div className={styles.actions}>
              <button
                type="button"
                className={styles.cancelBtn}
                onClick={onClose}
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className={styles.submitBtn}
                disabled={pin.length !== 4 || isLoading}
              >
                {isLoading ? 'Verifying...' : 'Verify PIN'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
