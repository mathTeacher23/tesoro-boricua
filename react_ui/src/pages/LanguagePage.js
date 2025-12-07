import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import AlphabetNavigation from '../components/AlphabetNavigation';
import TranslationSidebar from '../components/TranslationSidebar';
import LLMChatSidebar from '../components/LLMChatSidebar.js';

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
  const [chatSidebarOpen, setChatSidebarOpen] = useState(false);
  const [firstSidebarOpened, setFirstSidebarOpened] = useState(null); // 'translation' or 'chat'

  // Load data from API (new structure: letter/word.json)
  const loadDataForLetter = async (letter) => {
    try {
      // Fetch from new API endpoint
      const response = await fetch(`http://localhost:8000/api/dictionary/letter/${letter.toLowerCase()}`);

      if (!response.ok) {
        console.error(`Failed to load data for letter ${letter}`);
        return [];
      }

      const result = await response.json();
      const data = result.words || [];

      // Also load dialecto data if available (keep old structure for now)
      try {
        const dialectoResponse = await fetch(`/data/translated_dialecto/dialecto_letter_${letter.toUpperCase()}.json`);
        if (dialectoResponse.ok) {
          const dialectoData = await dialectoResponse.json();
          const dialectoEntries = dialectoData.map(item => ({
            ...item,
            file_source: 'Dialecto',
            data_version: 'V1',
            has_overlap: false
          }));
          data.push(...dialectoEntries);
        }
      } catch (dialectoError) {
        // Dialecto data is optional
        console.log(`No dialecto data for letter ${letter}`);
      }

      return data;
    } catch (error) {
      console.error(`Error loading data for letter ${letter}:`, error);
      return [];
    }
  };

  useEffect(() => {
    const checkAvailableLetters = async () => {
      try {
        // Fetch available letters from API
        const response = await fetch('http://localhost:8000/api/dictionary/letters');
        if (response.ok) {
          const data = await response.json();
          setAvailableLetters(data.letters || []);
        } else {
          console.error('Failed to fetch available letters');
          setAvailableLetters([]);
        }
      } catch (error) {
        console.error('Error fetching available letters:', error);
        setAvailableLetters([]);
      }
    };

    checkAvailableLetters();
  }, []);

  const applySourceFilter = (data) => {
    if (sourceFilter === 'all') return data;

    if (sourceFilter === 'tesoro') {
      return data.filter(item => item.file_source === 'Tesoro');
    } else if (sourceFilter === 'tesoro-v1') {
      return data.filter(item => item.file_source === 'Tesoro' && item.data_version === 'V1');
    } else if (sourceFilter === 'tesoro-v2') {
      return data.filter(item => item.file_source === 'Tesoro' && item.data_version === 'V2');
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

    try {
      // Use API search endpoint
      const response = await fetch(
        `http://localhost:8000/api/dictionary/search?query=${encodeURIComponent(searchQuery)}&search_type=${searchType}`
      );

      if (response.ok) {
        const data = await response.json();
        let searchResults = data.results || [];

        // Apply source filter
        const filteredResults = applySourceFilter(searchResults);
        setResults(filteredResults);
      } else {
        console.error('Search failed');
        setResults([]);
      }
    } catch (error) {
      console.error('Error searching:', error);
      setResults([]);
    }

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
      } else if (newSourceFilter === 'tesoro-v1') {
        return data.filter(item => item.file_source === 'Tesoro' && item.data_version === 'V1');
      } else if (newSourceFilter === 'tesoro-v2') {
        return data.filter(item => item.file_source === 'Tesoro' && item.data_version === 'V2');
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

  const groupAndDisplayResults = (results) => {
    // Group results by term (base word without superscript)
    const groupedByTerm = {};

    results.forEach((item, index) => {
      const baseTermKey = item.term;

      if (!groupedByTerm[baseTermKey]) {
        groupedByTerm[baseTermKey] = [];
      }

      groupedByTerm[baseTermKey].push({ ...item, originalIndex: index });
    });

    // Sort each group by superscript (numerically)
    Object.keys(groupedByTerm).forEach(term => {
      groupedByTerm[term].sort((a, b) => {
        const superscriptA = parseInt(a.superscript || '1');
        const superscriptB = parseInt(b.superscript || '1');
        return superscriptA - superscriptB;
      });
    });

    // Create grouped display
    return Object.keys(groupedByTerm)
      .sort()
      .map((term, termIndex) => {
        const variantsOfTerm = groupedByTerm[term];
        const hasMultipleVariants = variantsOfTerm.length > 1;

        return (
          <div key={`term-group-${termIndex}`} className="term-group">
            {hasMultipleVariants && (
              <div className="term-group-header">
                <h4>{term}</h4>
                <span className="variant-count">{variantsOfTerm.length} meaning{variantsOfTerm.length > 1 ? 's' : ''}</span>
              </div>
            )}

            <div className={hasMultipleVariants ? 'term-variants' : ''}>
              {variantsOfTerm.map((item, variantIndex) =>
                createDefinitionCard(item, variantIndex, hasMultipleVariants)
              )}
            </div>
          </div>
        );
      });
  };

  const createDefinitionCard = (item, index, isInGroup = false) => {
    const sourceClass = item.file_source === 'Tesoro' ? 'tesoro' : 'dialecto';
    const badgeClass = item.file_source === 'Tesoro' ? 'badge-tesoro' : 'badge-dialecto';
    const cardId = `${item.term}-${index}`;
    const isExpanded = expandedCards.has(cardId);
    const isV2 = item.data_version === 'V2';
    const stability = isV2 && item.consolidation_metadata?.definition_stability;
    const score = isV2 && item.consolidation_metadata?.semantic_similarity_score;

    return (
      <div key={index} className={`definition-card ${sourceClass} ${isExpanded ? 'expanded' : ''} ${isInGroup ? 'in-group' : ''}`}>
        <div
          className="card-header"
          onClick={() => toggleCard(cardId)}
          style={{ cursor: 'pointer' }}
        >
          <div className="term-title">
            {isInGroup ? (
              <>
                Meaning <sup className="superscript-large">{item.superscript || '1'}</sup>
              </>
            ) : (
              <>
                {item.term}
                {item.superscript && <sup>{item.superscript}</sup>}
              </>
            )}
            {item.has_overlap && (
              <span title="This term appears in both sources" style={{ color: '#ffc107' }}>
                🔄
              </span>
            )}
          </div>

          <div className="card-controls">
            <span className={`source-badge ${badgeClass}`}>
              {item.file_source} {item.data_version}
            </span>
            {isV2 && stability && (
              <span
                className="stability-badge"
                title={`Stability: ${stability}, Similarity: ${score}`}
                style={{
                  backgroundColor: stability.includes('High') ? '#4CAF50' : '#FFC107',
                  color: 'white',
                  padding: '2px 8px',
                  borderRadius: '12px',
                  fontSize: '0.75rem',
                  marginLeft: '4px'
                }}
              >
                ✓ {stability.includes('High') ? 'Reliable' : 'Moderate'}
              </span>
            )}
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

            {isV2 && item.consolidation_metadata && (
              <div className="metadata-section" style={{
                backgroundColor: '#f5f5f5',
                padding: '12px',
                marginTop: '12px',
                borderLeft: '4px solid #2196F3',
                borderRadius: '4px',
                fontSize: '0.85rem'
              }}>
                <h5>📊 Consolidation Metadata:</h5>
                <p><strong>Stability:</strong> {item.consolidation_metadata.definition_stability}</p>
                <p><strong>Similarity Score:</strong> {item.consolidation_metadata.semantic_similarity_score?.toFixed(2)}</p>
                <p><strong>Definitions Analyzed:</strong> {item.consolidation_metadata.num_definitions_analyzed}</p>
                {item.consolidation_metadata.themes && item.consolidation_metadata.themes.length > 0 && (
                  <p><strong>Themes:</strong> {item.consolidation_metadata.themes.slice(0, 3).join(', ')}</p>
                )}
                {item.consolidation_metadata.related_words && item.consolidation_metadata.related_words.length > 0 && (
                  <p><strong>Related Words:</strong> {item.consolidation_metadata.related_words.slice(0, 3).join(', ')}</p>
                )}
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
        onToggle={() => {
          if (!sidebarOpen && !chatSidebarOpen) {
            // First sidebar being opened
            setFirstSidebarOpened('translation');
          } else if (sidebarOpen && chatSidebarOpen) {
            // Closing the first sidebar while second is open
            setFirstSidebarOpened('chat');
          } else if (sidebarOpen && !chatSidebarOpen) {
            // Closing the only open sidebar
            setFirstSidebarOpened(null);
          }
          setSidebarOpen(!sidebarOpen);
        }}
        otherSidebarOpen={chatSidebarOpen}
        isFirst={firstSidebarOpened === 'translation'}
      />

      {/* LLM Chat Sidebar */}
      <LLMChatSidebar
        isOpen={chatSidebarOpen}
        onToggle={() => {
          if (!chatSidebarOpen && !sidebarOpen) {
            // First sidebar being opened
            setFirstSidebarOpened('chat');
          } else if (chatSidebarOpen && sidebarOpen) {
            // Closing the first sidebar while second is open
            setFirstSidebarOpened('translation');
          } else if (chatSidebarOpen && !sidebarOpen) {
            // Closing the only open sidebar
            setFirstSidebarOpened(null);
          }
          setChatSidebarOpen(!chatSidebarOpen);
        }}
        otherSidebarOpen={sidebarOpen}
        isFirst={firstSidebarOpened === 'chat'}
      />

      <div className="page-content" style={{ marginTop: '2rem' }}>
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
              <option value="tesoro">Tesoro (All versions)</option>
              <option value="tesoro-v1">Tesoro V1 (Original)</option>
              <option value="tesoro-v2">Tesoro V2 (Consolidated)</option>
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

            {results.some(r => r.data_version === 'V2') && (
              <div className="version-info" style={{ marginTop: '8px', fontSize: '0.9rem', color: '#666' }}>
                <span>V2 consolidated: {results.filter(r => r.data_version === 'V2').length}</span>
                {results.some(r => r.data_version === 'V1') && (
                  <span style={{ marginLeft: '16px' }}>V1 original: {results.filter(r => r.data_version === 'V1').length}</span>
                )}
              </div>
            )}

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
            groupAndDisplayResults(results)
          )}
        </div>
      </div>
    </div>
  );
};

export default LanguagePage;