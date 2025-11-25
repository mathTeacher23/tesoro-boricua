import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import AlphabetNavigation from '../components/AlphabetNavigation';
import TranslationSidebar from '../components/TranslationSidebar';

const LanguagePage = () => {
  const { letter } = useParams();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('partial');
  const [sourceFilter, setSourceFilter] = useState('all');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedLetter, setSelectedLetter] = useState(letter ? letter.toUpperCase() : null);
  const [availableLetters, setAvailableLetters] = useState([]);
  const [expandedCards, setExpandedCards] = useState(new Set());
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Load data from translated JSON files (they have English definitions)
  const loadDataForLetter = async (letter) => {
    try {
      const tesoroResponse = await fetch(`/data/translated_tesoro/transformed_tesoro_letter_${letter.toLowerCase()}.json`);
      const dialectoResponse = await fetch(`/data/translated_dialecto/dialecto_letter_${letter.toUpperCase()}.json`);

      const data = [];

      if (tesoroResponse.ok) {
        const tesoroData = await tesoroResponse.json();
        const tesoroEntries = tesoroData.map(item => ({
          ...item,
          file_source: 'Tesoro',
          has_overlap: false
        }));
        data.push(...tesoroEntries);
      }

      if (dialectoResponse.ok) {
        const dialectoData = await dialectoResponse.json();
        const dialectoEntries = dialectoData.map(item => ({
          ...item,
          file_source: 'Dialecto',
          has_overlap: false
        }));
        data.push(...dialectoEntries);
      }

      return data;
    } catch (error) {
      console.error(`Error loading data for letter ${letter}:`, error);
      return [];
    }
  };

  useEffect(() => {
    const checkAvailableLetters = async () => {
      // Only check available letters, don't load any data initially
      const alphabet = 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ'.split('');
      const lettersWithData = [];

      for (const letter of alphabet) {
        try {
          const tesoroResponse = await fetch(`/data/translated_tesoro/transformed_tesoro_letter_${letter.toLowerCase()}.json`, { method: 'HEAD' });
          const dialectoResponse = await fetch(`/data/translated_dialecto/dialecto_letter_${letter.toUpperCase()}.json`, { method: 'HEAD' });

          if (tesoroResponse.ok || dialectoResponse.ok) {
            lettersWithData.push(letter);
          }
        } catch (error) {
          // File doesn't exist, continue
        }
      }

      setAvailableLetters(lettersWithData);
    };

    checkAvailableLetters();
  }, []);

  const applySourceFilter = (data) => {
    if (sourceFilter === 'all') return data;

    if (sourceFilter === 'tesoro') {
      return data.filter(item => item.file_source === 'Tesoro');
    } else if (sourceFilter === 'dialecto') {
      return data.filter(item => item.file_source === 'Dialecto');
    } else if (sourceFilter === 'overlap') {
      return data.filter(item => item.has_overlap);
    }

    return data;
  };

  const handleLetterSelect = async (letter) => {
    setSelectedLetter(letter);
    setSearchQuery(''); // Clear search when browsing by letter
    setExpandedCards(new Set()); // Collapse all cards when selecting new letter

    if (letter) {
      setLoading(true);
      navigate(`/language/${letter.toLowerCase()}`);

      // Load data for the selected letter
      const letterData = await loadDataForLetter(letter);
      // Apply source filter to the letter data
      const filteredData = applySourceFilter(letterData);
      setResults(filteredData);
      setLoading(false);
    } else {
      navigate('/language');
      setResults([]);
    }
  };

  // Handle URL parameter changes
  useEffect(() => {
    const loadLetterFromURL = async () => {
      if (letter && availableLetters.length > 0) {
        const upperLetter = letter.toUpperCase();
        setSelectedLetter(upperLetter);
        setLoading(true);
        const letterData = await loadDataForLetter(upperLetter);
        const filteredData = applySourceFilter(letterData);
        setResults(filteredData);
        setLoading(false);
      } else if (!letter) {
        setSelectedLetter(null);
        setResults([]);
      }
    };

    loadLetterFromURL();
  }, [letter, availableLetters, sourceFilter]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setSelectedLetter(null);
    navigate('/language');

    // Search across all available letters
    const searchResults = [];
    for (const searchLetter of availableLetters) {
      const letterData = await loadDataForLetter(searchLetter);
      searchResults.push(...letterData);
    }

    // Apply source filter first
    let filteredResults = applySourceFilter(searchResults);

    // Apply search query
    const query = searchQuery.toLowerCase();
    filteredResults = filteredResults.filter(item => {
      const term = item.term.toLowerCase();
      const esText = item.es_definitions.join(' ').toLowerCase();
      const enText = item.en_definitions.join(' ').toLowerCase();

      switch (searchType) {
        case 'exact':
          return term === query;
        case 'partial':
          return term.includes(query);
        case 'contains':
          return term.includes(query) || esText.includes(query) || enText.includes(query);
        default:
          return term.includes(query);
      }
    });

    setResults(filteredResults);
    setLoading(false);
  };

  const handleClear = () => {
    setSearchQuery('');
    setSelectedLetter(null);
    navigate('/language');
    setResults([]);
  };

  const handleSourceFilterChange = async (newSourceFilter) => {
    setSourceFilter(newSourceFilter);

    // Helper function to apply the new filter
    const applyNewSourceFilter = (data) => {
      if (newSourceFilter === 'all') return data;

      if (newSourceFilter === 'tesoro') {
        return data.filter(item => item.file_source === 'Tesoro');
      } else if (newSourceFilter === 'dialecto') {
        return data.filter(item => item.file_source === 'Dialecto');
      } else if (newSourceFilter === 'overlap') {
        return data.filter(item => item.has_overlap);
      }

      return data;
    };

    // If we have a selected letter, reapply the filter to current letter data
    if (selectedLetter) {
      setLoading(true);
      const letterData = await loadDataForLetter(selectedLetter);
      const filteredData = applyNewSourceFilter(letterData);
      setResults(filteredData);
      setLoading(false);
    }
    // If we have search results, we need to re-run the search with the new filter
    else if (searchQuery.trim()) {
      // Wait for the state to update, then re-run search
      setTimeout(() => {
        handleSearch();
      }, 0);
    }
  };

  const toggleCard = (cardId) => {
    const newExpanded = new Set(expandedCards);
    if (newExpanded.has(cardId)) {
      newExpanded.delete(cardId);
    } else {
      newExpanded.add(cardId);
    }
    setExpandedCards(newExpanded);
  };

  const createDefinitionCard = (item, index) => {
    const sourceClass = item.file_source === 'Tesoro' ? 'tesoro' : 'dialecto';
    const badgeClass = item.file_source === 'Tesoro' ? 'badge-tesoro' : 'badge-dialecto';
    const cardId = `${item.term}-${index}`;
    const isExpanded = expandedCards.has(cardId);

    return (
      <div key={index} className={`definition-card ${sourceClass} ${isExpanded ? 'expanded' : ''}`}>
        <div
          className="card-header"
          onClick={() => toggleCard(cardId)}
          style={{ cursor: 'pointer' }}
        >
          <div className="term-title">
            {item.term}
            {item.has_overlap && (
              <span title="This term appears in both sources" style={{ color: '#ffc107' }}>
                🔄
              </span>
            )}
          </div>

          <div className="card-controls">
            <span className={`source-badge ${badgeClass}`}>{item.file_source}</span>
            <span className="expand-icon">
              {isExpanded ? '▼' : '▶'}
            </span>
          </div>
        </div>

        {isExpanded && (
          <div className="card-content">
            <div className="definition-section">
              <h5>🇪🇸 Español:</h5>
              <div className="spanish-def">
                {item.es_definitions.map((def, idx) => (
                  <div key={idx} className="definition-item">{def}</div>
                ))}
              </div>
            </div>

            {item.en_definitions && item.en_definitions.length > 0 && (
              <div className="definition-section">
                <h5>🇺🇸 English:</h5>
                <div className="english-def">
                  {item.en_definitions.map((def, idx) => (
                    <div key={idx} className="definition-item">{def}</div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="container">
      <Link to="/" className="back-button">
        <i className="fas fa-arrow-left"></i> Back to Home
      </Link>

      {/* Translation Sidebar */}
      <TranslationSidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />

      <div className="page-content">
        <div className="page-header">
          <h2>📖 Language & Words</h2>
          <p>Explore Puerto Rican Spanish words, phrases, and expressions from multiple sources.</p>
        </div>

        {/* Alphabet Navigation */}
        <AlphabetNavigation
          selectedLetter={selectedLetter}
          onLetterSelect={handleLetterSelect}
          availableLetters={availableLetters}
        />

        {/* Search Section */}
        <div className="search-section">
          <div className="search-form">
            <input
              type="text"
              className="search-input"
              placeholder="e.g., 'fuego', 'chavos', 'culcul'"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>

          <div className="search-filters">
            <select
              value={searchType}
              onChange={(e) => setSearchType(e.target.value)}
            >
              <option value="partial">Partial match (recommended)</option>
              <option value="exact">Exact term only</option>
              <option value="contains">Search in definitions</option>
            </select>

            <select
              value={sourceFilter}
              onChange={(e) => handleSourceFilterChange(e.target.value)}
            >
              <option value="all">All sources</option>
              <option value="tesoro">Tesoro (Dictionary)</option>
              <option value="dialecto">Dialecto (Cultural)</option>
              <option value="overlap">Overlapping terms</option>
            </select>
          </div>

          <div className="search-controls">
            <button className="btn btn-primary" onClick={handleSearch} disabled={loading}>
              <i className="fas fa-search"></i> {loading ? 'Searching...' : 'Search'}
            </button>
            <button className="btn btn-secondary" onClick={handleClear}>
              <i className="fas fa-eraser"></i> Clear
            </button>
          </div>
        </div>

        {/* Results Summary */}
        {results.length > 0 && (
          <div className="results-summary">
            <strong>Found {results.length} {results.length === 1 ? 'word' : 'words'}</strong>
            {selectedLetter && ` starting with "${selectedLetter}"`}
            {searchQuery && ` for "${searchQuery}"`}
            {sourceFilter !== 'all' && ` in ${sourceFilter} source`}
            <div className="results-hint">
              💡 Click on any word to see its definitions
            </div>
          </div>
        )}

        {/* Results Display */}
        <div className="results-container">
          {loading ? (
            <div className="loading-message">
              <h3>🔄 Loading words...</h3>
              <p>Please wait while we fetch the data.</p>
            </div>
          ) : results.length === 0 ? (
            <div className="no-results">
              <h3>🔍 {selectedLetter ? `No words found for letter "${selectedLetter}"` : searchQuery ? 'No results found' : 'Select a letter to browse words'}</h3>
              <p>{selectedLetter ? 'Try selecting a different letter.' : searchQuery ? 'Try adjusting your search query or search type.' : 'Click on any letter above to see available words.'}</p>
            </div>
          ) : (
            results.map((item, index) => createDefinitionCard(item, index))
          )}
        </div>
      </div>
    </div>
  );
};

export default LanguagePage;