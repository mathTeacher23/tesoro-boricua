import React from 'react';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const navigate = useNavigate();

  const handleHomeClick = () => {
    navigate('/');
  };

  return (
    <header className="header">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <button
          onClick={handleHomeClick}
          title="Go to Home"
          style={{
            background: 'transparent',
            border: 'none',
            color: '#fff',
            cursor: 'pointer',
            fontSize: '1.5rem',
            padding: '0.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            transition: 'opacity 0.2s ease'
          }}
          onMouseEnter={(e) => (e.target.style.opacity = '0.8')}
          onMouseLeave={(e) => (e.target.style.opacity = '1')}
        >
          <i className="fas fa-home"></i>
        </button>
        <h1>🇵🇷 Tesoro Boricua - Puerto Rican Cultural Learning Platform</h1>
        <div style={{ width: '2.5rem' }}></div>
      </div>
    </header>
  );
};

export default Header;