import React, { useState } from 'react';

const TranslationSidebar = ({ isOpen, onToggle }) => {
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
      <button
        className={`translation-toggle ${isOpen ? 'open' : ''}`}
        onClick={onToggle}
        title="Toggle Translation Sidebar"
      >
        <i className="fas fa-language"></i>
        {isOpen ? ' Close' : ' Translate'}
      </button>

      {/* Sidebar */}
      <div className={`translation-sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h3>
            <i className="fas fa-language"></i>
            Quick Translation
          </h3>
          <button className="close-btn" onClick={onToggle}>
            <i className="fas fa-times"></i>
          </button>
        </div>

        <div className="sidebar-content">
          {/* Language Selection */}
          <div className="language-controls">
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
              title="Swap languages"
              disabled={fromLang === 'auto'}
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

          {/* Input Text */}
          <div className="translation-input">
            <label>Enter text to translate:</label>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type your text here..."
              rows={4}
              maxLength={500}
            />
            <div className="char-count">
              {inputText.length}/500
            </div>
          </div>

          {/* Translation Controls */}
          <div className="translation-controls">
            <button
              className="btn btn-primary"
              onClick={handleTranslate}
              disabled={isTranslating || !inputText.trim()}
            >
              <i className={`fas ${isTranslating ? 'fa-spinner fa-spin' : 'fa-language'}`}></i>
              {isTranslating ? 'Translating...' : 'Translate'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleClear}
            >
              <i className="fas fa-eraser"></i>
              Clear
            </button>
          </div>

          {/* Error Display */}
          {error && (
            <div className="translation-error">
              <i className="fas fa-exclamation-triangle"></i>
              {error}
            </div>
          )}

          {/* Translation Result */}
          {translatedText && (
            <div className="translation-result">
              <label>Translation:</label>
              <div className="result-text">
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

          {/* Help Text */}
          <div className="translation-help">
            <p>
              <i className="fas fa-info-circle"></i>
              <strong>Quick tip:</strong> Use this tool to translate words or phrases between English and Spanish while browsing the dictionary.
            </p>
          </div>
        </div>
      </div>

      {/* Backdrop */}
      {isOpen && <div className="sidebar-backdrop" onClick={onToggle}></div>}
    </>
  );
};

export default TranslationSidebar;