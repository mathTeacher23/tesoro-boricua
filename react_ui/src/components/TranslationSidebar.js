import React, { useState } from 'react';
import { colors } from '../config/colors';

const TranslationSidebar = ({ isOpen, onToggle, otherSidebarOpen, isFirst }) => {
  const [inputText, setInputText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [fromLang, setFromLang] = useState('en');
  const [toLang, setToLang] = useState('es');
  const [isTranslating, setIsTranslating] = useState(false);
  const [error, setError] = useState(null);

  const API_BASE_URL = 'http://localhost:8000';

  const handleTranslate = async () => {
    if (!inputText.trim()) {
      setError('Please enter text to translate');
      return;
    }

    setIsTranslating(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/translate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          from_lang: fromLang,
          to_lang: toLang,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Translation failed');
      }

      const data = await response.json();
      setTranslatedText(data.translated_text);
    } catch (err) {
      console.error('Translation error:', err);
      setError(err.message || 'Failed to translate. Make sure the translation server is running.');
    } finally {
      setIsTranslating(false);
    }
  };

  const handleSwapLanguages = () => {
    setFromLang(toLang);
    setToLang(fromLang);
    setInputText(translatedText);
    setTranslatedText(inputText);
  };

  const handleClear = () => {
    setInputText('');
    setTranslatedText('');
    setError(null);
  };

  return (
    <>
      {/* Toggle Button */}
      {!isOpen && (
        <button
          onClick={onToggle}
          title="Toggle Translation Sidebar"
          style={{
            position: 'fixed',
            top: '70px',
            right: otherSidebarOpen ? '370px' : '10px',
            borderRadius: '0 0 8px 0',
            zIndex: '1001',
            padding: '12px 16px',
            height: '44px',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            transition: 'right 0.3s ease-in-out',
            background: colors.translateSidebarBg,
            color: '#fff',
            border: 'none',
            cursor: 'pointer',
            fontSize: '0.9rem',
            fontWeight: '500'
          }}
        >
          <i className="fas fa-language"></i> Translate
        </button>
      )}

      {/* Sidebar */}
      <div
        className={`translation-sidebar ${isOpen ? 'open' : ''}`}
        data-sidebar="translation"
        style={{
          position: 'fixed',
          right: isOpen ? (isFirst ? '0' : '350px') : '-350px',
          top: '70px',
          height: '93vh', /* had to shift this down since anchoring header*/
          width: '350px',
          zIndex: isFirst ? '1000' : '999',
          transition: 'right 0.3s ease-in-out',
          boxShadow: '-2px 0 10px rgba(0,0,0,0.1)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          background: '#fff'
        }}
      >
        <div className="sidebar-header">
          <h3>
            
            Translate <i className="fas fa-language"></i>
          </h3>
          <button className="close-btn" onClick={onToggle}>
            <i className="fas fa-times"></i>
          </button>
        </div>

        {/* Content Area with Scrollable Results */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1rem', paddingRight: '4px' }}>
          {/* Language Selection */}
          <div className="language-controls" style={{ marginBottom: '1rem' }}>
            <div className="language-selector">
              <label>From:</label>
              <select
                value={fromLang}
                onChange={(e) => setFromLang(e.target.value)}
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="auto">Auto-detect</option>
              </select>
            </div>

            <button
              className="swap-btn"
              onClick={handleSwapLanguages}
              title="Swap languages and texts"
              disabled={fromLang === 'auto'}
              style={{ cursor: fromLang === 'auto' ? 'not-allowed' : 'pointer' }}
            >
              <i className="fas fa-exchange-alt"></i>
            </button>

            <div className="language-selector">
              <label>To:</label>
              <select
                value={toLang}
                onChange={(e) => setToLang(e.target.value)}
              >
                <option value="es">Spanish</option>
                <option value="en">English</option>
              </select>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="translation-error" style={{ marginBottom: '1rem' }}>
              <i className="fas fa-exclamation-triangle"></i>
              {error}
            </div>
          )}

          {/* Translation Result */}
          {translatedText && (
            <div className="translation-result" style={{ marginBottom: '1rem' }}>
              <label>Translation:</label>
              <div className="result-text" style={{ padding: '0.75rem', background: '#f8f9fa', borderRadius: '6px', marginBottom: '0.5rem', minHeight: '40px' }}>
                {translatedText}
              </div>
              <button
                className="copy-btn"
                onClick={() => navigator.clipboard.writeText(translatedText)}
                title="Copy to clipboard"
              >
                <i className="fas fa-copy"></i>
                Copy
              </button>
            </div>
          )}

        </div>

        {/* Input Area - Anchored to Bottom */}
        <div style={{ borderTop: '1px solid #dee2e6', padding: '1rem', background: '#fff' }}>
          <div className="translation-input" style={{ marginBottom: '0.5rem' }}>
            <label style={{ fontSize: '0.9rem', marginBottom: '0.5rem', display: 'block' }}>Enter text to translate:</label>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type your text here..."
              rows={3}
              maxLength={500}
              style={{ width: '100%', borderRadius: '6px', border: '1px solid #dee2e6', padding: '0.5rem', fontFamily: 'inherit', resize: 'none' }}
            />
            <div className="char-count" style={{ fontSize: '0.75rem', color: '#6c757d', marginTop: '0.25rem' }}>
              {inputText.length}/500
            </div>
          </div>

          {/* Translation Controls */}
          <div className="translation-controls" style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              className="btn btn-primary"
              onClick={handleTranslate}
              disabled={isTranslating || !inputText.trim()}
              title="Translate text between English and Spanish"
              style={{ flex: 1, padding: '0.5rem 1rem', background: '#007bff', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
            >
              <i className={`fas ${isTranslating ? 'fa-spinner fa-spin' : 'fa-language'}`}></i>
              {isTranslating ? 'Translating...' : 'Translate'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleClear}
              title="Clear all text and results"
              style={{ flex: 1, padding: '0.5rem 1rem', background: '#6c757d', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
            >
              <i className="fas fa-eraser"></i>
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Backdrop */}
      {isOpen && (
        <div
          style={{
            position: 'fixed',
            top: '0',
            left: '0',
            right: '350px',
            bottom: '0',
            background: 'rgba(0, 0, 0, 0.3)',
            zIndex: '998',
            onClick: onToggle
          }}
        ></div>
      )}
    </>
  );
};

export default TranslationSidebar;