// DEMO TOGGLE COMPONENT - FOR TESTING ONLY
// TODO: Remove this component before production deployment

import { useState, useEffect } from 'react';
import styles from './DemoToggle.module.css';

export const DemoToggle = () => {
  const [demoMode, setDemoMode] = useState(() => {
    return localStorage.getItem('DEMO_MODE') === 'true';
  });

  useEffect(() => {
    localStorage.setItem('DEMO_MODE', demoMode);
    // Reload to apply changes
  }, [demoMode]);

  const handleToggle = () => {
    const newMode = !demoMode;
    setDemoMode(newMode);

    // Show alert
    if (newMode) {
      alert('🎭 Demo Mode ENABLED\n\n✅ All backend calls will use mock data\n✅ Test PIN: 1234\n\nRefresh the page to apply changes.');
    } else {
      alert('🌐 Demo Mode DISABLED\n\n✅ Backend calls will use real API\n\nRefresh the page to apply changes.');
    }

    // Reload page to apply changes
    window.location.reload();
  };

  return (
    <div className={styles.container}>
      <button
        className={`${styles.toggleBtn} ${demoMode ? styles.active : ''}`}
        onClick={handleToggle}
        title={demoMode ? 'Demo Mode ON (using mock data)' : 'Demo Mode OFF (using real API)'}
      >
        {demoMode ? '🎭 DEMO' : '🌐 LIVE'}
      </button>
      {demoMode && (
        <div className={styles.badge}>
          Demo Mode Active
        </div>
      )}
    </div>
  );
};
