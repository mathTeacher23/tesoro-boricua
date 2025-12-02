import React from 'react';
import { Link } from 'react-router-dom';
import { creatorBio } from '../config/bio';

const CreatorBioPage = () => {
  const paragraphStyle = { lineHeight: '1.6', color: '#333', marginBottom: '1rem' };
  const lastParagraphStyle = { ...paragraphStyle, marginBottom: 0 };

  return (
    <div className="container">
      <Link to="/" className="back-button">
        <i className="fas fa-arrow-left"></i> Back to Home
      </Link>

      <div className="page-content">
        <div className="page-header">
          <h2>Creator Bio</h2>
          <p>Learn about the creator of Tesoro Boricua</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginTop: '2rem' }}>
          {/* English Bio */}
          <div style={{ padding: '1.5rem', background: '#f8f9fa', borderRadius: '8px', border: '1px solid #dee2e6' }}>
            <h3 style={{ color: '#007bff', marginBottom: '1rem', fontSize: '1.3rem' }}>🇺🇸 English</h3>

            <h4 style={{ marginTop: '1.5rem', marginBottom: '0.75rem', color: '#2c3e50' }}>About Me</h4>
            {creatorBio.english.aboutMe.map((paragraph, idx) => (
              <p
                key={`en-about-${idx}`}
                style={idx === creatorBio.english.aboutMe.length - 1 ? lastParagraphStyle : paragraphStyle}
              >
                {paragraph}
              </p>
            ))}

            <h4 style={{ marginTop: '1.5rem', marginBottom: '0.75rem', color: '#2c3e50' }}>My Motivation for This Project</h4>
            {creatorBio.english.motivation.map((paragraph, idx) => (
              <p
                key={`en-motivation-${idx}`}
                style={idx === creatorBio.english.motivation.length - 1 ? lastParagraphStyle : paragraphStyle}
              >
                {paragraph}
              </p>
            ))}

            {creatorBio.english.signature && creatorBio.english.signature.length > 0 && (
              <p style={{ marginTop: '1.5rem', fontStyle: 'italic', color: '#666' }}>
                {creatorBio.english.signature[0]}
              </p>
            )}
          </div>

          {/* Spanish Bio */}
          <div style={{ padding: '1.5rem', background: '#f9f6ff', borderRadius: '8px', border: '1px solid #dee2e6' }}>
            <h3 style={{ color: '#22c55e', marginBottom: '1rem', fontSize: '1.3rem' }}>🇵🇷 Español</h3>

            <h4 style={{ marginTop: '1.5rem', marginBottom: '0.75rem', color: '#2c3e50' }}>Sobre mí</h4>
            {creatorBio.spanish.aboutMe.map((paragraph, idx) => (
              <p
                key={`es-about-${idx}`}
                style={idx === creatorBio.spanish.aboutMe.length - 1 ? lastParagraphStyle : paragraphStyle}
              >
                {paragraph}
              </p>
            ))}

            <h4 style={{ marginTop: '1.5rem', marginBottom: '0.75rem', color: '#2c3e50' }}>Mi motivación para este proyecto</h4>
            {creatorBio.spanish.motivation.map((paragraph, idx) => (
              <p
                key={`es-motivation-${idx}`}
                style={idx === creatorBio.spanish.motivation.length - 1 ? lastParagraphStyle : paragraphStyle}
              >
                {paragraph}
              </p>
            ))}

            {creatorBio.spanish.signature && creatorBio.spanish.signature.length > 0 && (
              <p style={{ marginTop: '1.5rem', fontStyle: 'italic', color: '#666' }}>
                {creatorBio.spanish.signature[0]}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreatorBioPage;
