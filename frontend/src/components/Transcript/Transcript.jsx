import styles from './Transcript.module.css';

export const Transcript = ({ messages, onClear }) => {
  if (!messages || messages.length === 0) {
    return null;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.title}>Conversation</span>
        <button className={styles.clearBtn} onClick={onClear}>
          Clear
        </button>
      </div>
      <div className={styles.messages}>
        {messages.map((msg, idx) => (
          <div key={idx} className={`${styles.message} ${styles[msg.type]}`}>
            <div className={styles.messageAvatar}>
              {msg.type === 'user' ? '👤' : '🤖'}
            </div>
            <div className={styles.messageBubble}>
              <p>{msg.text}</p>
              {msg.timestamp && (
                <span className={styles.timestamp}>
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
