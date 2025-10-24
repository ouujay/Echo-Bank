import styles from './ConfirmModal.module.css';

export const ConfirmModal = ({ onClose, onConfirm, transferData, isLoading, isSuccess }) => {
  if (isSuccess && transferData) {
    return (
      <div className={styles.overlay} onClick={onClose}>
        <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
          <div className={styles.successContent}>
            <div className={styles.successIcon}>✓</div>
            <h2 className={styles.successTitle}>Transfer Successful!</h2>

            <div className={styles.successDetails}>
              <div className={styles.detailRow}>
                <span className={styles.label}>Recipient:</span>
                <span className={styles.value}>{transferData.recipient?.name}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.label}>Amount:</span>
                <span className={styles.successAmount}>₦{transferData.amount?.toLocaleString()}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.label}>Reference:</span>
                <span className={styles.value}>{transferData.transaction_ref}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.label}>New Balance:</span>
                <span className={styles.value}>₦{transferData.new_balance?.toLocaleString()}</span>
              </div>
            </div>

            <button className={styles.doneBtn} onClick={onClose}>
              Done
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h2>Confirm Transfer</h2>
          <button className={styles.closeBtn} onClick={onClose}>×</button>
        </div>

        <div className={styles.content}>
          <div className={styles.warningBanner}>
            <span className={styles.warningIcon}>⚠️</span>
            <p>Please review the details before confirming</p>
          </div>

          {transferData && (
            <div className={styles.details}>
              <div className={styles.detailRow}>
                <span className={styles.label}>Recipient:</span>
                <span className={styles.value}>{transferData.recipient?.name}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.label}>Account Number:</span>
                <span className={styles.value}>{transferData.recipient?.account_number}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.label}>Bank:</span>
                <span className={styles.value}>{transferData.recipient?.bank_name}</span>
              </div>
              <div className={styles.separator}></div>
              <div className={styles.detailRow}>
                <span className={styles.label}>Amount:</span>
                <span className={styles.amount}>₦{transferData.amount?.toLocaleString()}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.label}>Current Balance:</span>
                <span className={styles.value}>₦{transferData.current_balance?.toLocaleString()}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.label}>New Balance:</span>
                <span className={styles.newBalance}>₦{transferData.new_balance?.toLocaleString()}</span>
              </div>
            </div>
          )}

          <div className={styles.actions}>
            <button
              className={styles.cancelBtn}
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              className={styles.confirmBtn}
              onClick={onConfirm}
              disabled={isLoading}
            >
              {isLoading ? 'Processing...' : 'Confirm Transfer'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
