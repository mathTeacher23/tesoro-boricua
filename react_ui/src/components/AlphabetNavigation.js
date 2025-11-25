import React from 'react';

const AlphabetNavigation = ({ selectedLetter, onLetterSelect, availableLetters }) => {
  const alphabet = 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ'.split('');

  return (
    <div className="alphabet-navigation">
      <h4>Browse by Letter:</h4>
      <div className="letter-grid">
        {alphabet.map(letter => {
          const isAvailable = availableLetters.includes(letter);
          const isSelected = selectedLetter === letter;

          return (
            <button
              key={letter}
              className={`letter-btn ${isSelected ? 'selected' : ''} ${!isAvailable ? 'disabled' : ''}`}
              onClick={() => isAvailable && onLetterSelect(letter)}
              disabled={!isAvailable}
              title={isAvailable ? `Browse words starting with ${letter}` : `No words available for ${letter}`}
            >
              {letter}
            </button>
          );
        })}
      </div>
      {selectedLetter && (
        <div className="letter-info">
          <span>Showing words starting with <strong>{selectedLetter}</strong></span>
          <button
            className="clear-letter-btn"
            onClick={() => onLetterSelect(null)}
            title="Show all words"
          >
            Show All
          </button>
        </div>
      )}
    </div>
  );
};

export default AlphabetNavigation;