import React, { useState } from 'react';
import './RecipeContent.css';

const RecipeContent = ({ recipeDetails, containerStyle = {}, contentStyle = {} }) => {
  const [activeTab, setActiveTab] = useState('ingredients');

  if (!recipeDetails) {
    return (
      <div className="recipe-content-container">
        <div className="loading-content">
          <p>Loading recipe details...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="recipe-content-container" style={containerStyle}>
      <div className="recipe-tabs">
        <button
          className={`tab-button ${activeTab === 'ingredients' ? 'active' : ''}`}
          onClick={() => setActiveTab('ingredients')}
        >
          <i className="fas fa-list"></i> Ingredients
        </button>
        <button
          className={`tab-button ${activeTab === 'instructions' ? 'active' : ''}`}
          onClick={() => setActiveTab('instructions')}
        >
          <i className="fas fa-tasks"></i> Instructions
        </button>
        {recipeDetails.notes && recipeDetails.notes.length > 0 && (
          <button
            className={`tab-button ${activeTab === 'notes' ? 'active' : ''}`}
            onClick={() => setActiveTab('notes')}
          >
            <i className="fas fa-sticky-note"></i> Notes
          </button>
        )}
        {recipeDetails.lessonsLearned && recipeDetails.lessonsLearned.length > 0 && (
          <button
            className={`tab-button ${activeTab === 'lessons' ? 'active' : ''}`}
            onClick={() => setActiveTab('lessons')}
          >
            <i className="fas fa-lightbulb"></i> Tips
          </button>
        )}
      </div>

      <div className="tab-content">
        {activeTab === 'ingredients' && (
          <div className="ingredients-section">
            <h3>🛒 Ingredients</h3>
            <div className="ingredients-list">
              {recipeDetails.ingredients.map((ingredient, index) => (
                <div key={index} className="ingredient-item">
                  <i className="fas fa-check"></i>
                  <span>{ingredient}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'instructions' && (
          <div className="instructions-section">
            <h3>👩‍🍳 Instructions</h3>
            <div className="instructions-list">
              {recipeDetails.instructions.map((instruction, index) => (
                <div key={index} className="instruction-item">
                  <div className="instruction-number">{index + 1}</div>
                  <div className="instruction-text">
                    {instruction.replace(/^\d+\.\s*/, '')}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'notes' && recipeDetails.notes && (
          <div className="notes-section">
            <h3>📝 Notes</h3>
            <div className="notes-content">
              {recipeDetails.notes.map((note, index) => (
                <p key={index}>{note}</p>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'lessons' && recipeDetails.lessonsLearned && (
          <div className="lessons-section">
            <h3>💡 Lessons Learned & Tips</h3>
            <div className="lessons-list">
              {recipeDetails.lessonsLearned.map((lesson, index) => (
                <div key={index} className="lesson-item">
                  <i className="fas fa-lightbulb"></i>
                  <span>{lesson}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecipeContent;