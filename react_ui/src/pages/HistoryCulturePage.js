import React from 'react';
import { Link } from 'react-router-dom';

const HistoryCulturePage = () => {
  return (
    <div className="container">
      <Link to="/" className="back-button">
        <i className="fas fa-arrow-left"></i> Back to Home
      </Link>

      <div className="page-content">
        <div className="page-header">
          <h2>📚 History & Culture</h2>
          <p>Dive deep into Puerto Rico's rich history and cultural heritage.</p>
        </div>

        <div style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🚧</div>
          <h3 style={{ color: '#6c757d', marginBottom: '0.5rem' }}>Coming Soon</h3>
          <p style={{ color: '#6c757d', marginBottom: '2rem' }}>
            This section is currently under construction. Check back soon for fascinating stories and insights into Puerto Rico's history and vibrant cultural heritage!
          </p>
          <Link to="/" className="btn btn-primary" style={{ display: 'inline-block', padding: '0.75rem 1.5rem', backgroundColor: '#007bff', color: '#fff', textDecoration: 'none', borderRadius: '6px' }}>
            Return to Home
          </Link>
        </div>
      </div>
    </div>
  );
};

export default HistoryCulturePage;
