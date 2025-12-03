import React, { useState, useEffect } from 'react';
import './ValidationApp.css';

const API_BASE = 'http://localhost:5001/api';

export default function ValidationApp() {
  const [letters, setLetters] = useState([]);
  const [selectedLetter, setSelectedLetter] = useState(null);
  const [words, setWords] = useState([]);
  const [filteredWords, setFilteredWords] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedWord, setSelectedWord] = useState(null);
  const [rawData, setRawData] = useState(null);
  const [preprocessedData, setPreprocessedData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [expandedLetters, setExpandedLetters] = useState({});

  // Load letters on component mount
  useEffect(() => {
    fetchLetters();
  }, []);

  const fetchLetters = async () => {
    try {
      const response = await fetch(`${API_BASE}/letters`);
      const data = await response.json();
      setLetters(data.letters);
    } catch (error) {
      console.error('Error fetching letters:', error);
    }
  };

  const fetchWords = async (letter) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/words/${letter}`);
      const data = await response.json();
      setWords(data.words || []);
      setFilteredWords(data.words || []);
    } catch (error) {
      console.error('Error fetching words:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLetterClick = (letter) => {
    if (selectedLetter === letter && expandedLetters[letter]) {
      setExpandedLetters({ ...expandedLetters, [letter]: false });
      setSelectedLetter(null);
      setWords([]);
      setFilteredWords([]);
    } else {
      setSelectedLetter(letter);
      setExpandedLetters({ ...expandedLetters, [letter]: true });
      fetchWords(letter);
    }
  };

  const handleSearch = (value) => {
    setSearchTerm(value);
    if (selectedLetter) {
      const filtered = words.filter(word =>
        word.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredWords(filtered);
    }
  };

  const fetchWordData = async (word) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/word-data?word=${encodeURIComponent(word)}`);
      const data = await response.json();
      setSelectedWord(word);
      setRawData(data.raw);
      setPreprocessedData(data.preprocessed);
    } catch (error) {
      console.error('Error fetching word data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleWordClick = (word) => {
    fetchWordData(word);
  };

  const renderJsonDisplay = (data, title) => {
    if (!data) {
      return <div className="data-section"><h3>{title}</h3><p>No data available</p></div>;
    }

    return (
      <div className="data-section">
        <h3>{title}</h3>
        <pre className="json-display">{JSON.stringify(data, null, 2)}</pre>
      </div>
    );
  };

  return (
    <div className="validation-app">
      <header className="app-header">
        <h1>TESORO Boricua - Word Validation</h1>
        <p>Compare raw and preprocessed word data</p>
      </header>

      <div className="main-content">
        {/* Left Panel - Search and Word List */}
        <div className="left-panel">
          <div className="search-section">
            <input
              type="text"
              className="search-bar"
              placeholder="Search words..."
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
            />
          </div>

          <div className="alphabet-section">
            <h3>Letters</h3>
            <div className="alphabet-grid">
              {letters.map(letter => (
                <div key={letter} className="letter-group">
                  <button
                    className={`letter-button ${selectedLetter === letter ? 'active' : ''} ${expandedLetters[letter] ? 'expanded' : ''}`}
                    onClick={() => handleLetterClick(letter)}
                  >
                    {letter.toUpperCase()}
                  </button>
                  {expandedLetters[letter] && (
                    <div className="words-list">
                      {loading ? (
                        <div className="loading">Loading...</div>
                      ) : filteredWords.length > 0 ? (
                        <ul>
                          {filteredWords.map((word, idx) => (
                            <li
                              key={idx}
                              className={selectedWord === word ? 'selected' : ''}
                              onClick={() => handleWordClick(word)}
                            >
                              {word}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="no-results">No words found</p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Panel - Data Display */}
        <div className="right-panel">
          {selectedWord ? (
            <>
              <div className="selected-word-header">
                <h2>{selectedWord}</h2>
              </div>
              <div className="data-container">
                <div className="data-column">
                  <h3>Raw Data</h3>
                  {rawData ? (
                    <pre className="json-display">{JSON.stringify(rawData, null, 2)}</pre>
                  ) : (
                    <p className="no-data">No raw data found</p>
                  )}
                </div>
                <div className="data-column">
                  <h3>Preprocessed Data</h3>
                  {preprocessedData ? (
                    <pre className="json-display">{JSON.stringify(preprocessedData, null, 2)}</pre>
                  ) : (
                    <p className="no-data">No preprocessed data found</p>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="placeholder">
              <p>Select a word from the left panel to view its data</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
