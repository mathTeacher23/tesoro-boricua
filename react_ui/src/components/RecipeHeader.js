import React from 'react';
import './RecipeHeader.css';

const RecipeHeader = ({ recipe, onPrint, containerStyle = {} }) => {
  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return '#28a745';
      case 'medium': return '#ffc107';
      case 'hard': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'Main Dish': return '🍽️';
      case 'Side Dish': return '🥘';
      case 'Appetizer': return '🥟';
      case 'Beverage': return '🥤';
      case 'Condiment': return '🧄';
      default: return '🍴';
    }
  };

  return (
    <div className="recipe-header-container" style={containerStyle}>
      <div className="recipe-image-section">
        <img
          src={recipe.image}
          alt={recipe.name}
          onError={(e) => {
            e.target.src = '/recipes/images/default-recipe.jpg';
          }}
        />
      </div>

      <div className="recipe-info-section">
        <div className="recipe-category-tag">
          {getCategoryIcon(recipe.category)} {recipe.category}
        </div>

        <h1 className="recipe-title">{recipe.name}</h1>
        <p className="recipe-description">{recipe.description}</p>

        <div className="recipe-meta-container">
          <div className="recipe-meta-item">
            <i className="fas fa-clock"></i>
            <div>
              <strong>Cooking Time</strong>
              <span>{recipe.cookingTime}</span>
            </div>
          </div>
          <div className="recipe-meta-item">
            <i className="fas fa-users"></i>
            <div>
              <strong>Servings</strong>
              <span>{recipe.servings}</span>
            </div>
          </div>
          <div className="recipe-meta-item">
            <i className="fas fa-signal"></i>
            <div>
              <strong>Difficulty</strong>
              <span
                className="difficulty-badge"
                style={{ backgroundColor: getDifficultyColor(recipe.difficulty) }}
              >
                {recipe.difficulty}
              </span>
            </div>
          </div>
        </div>

        <div className="recipe-actions">
          <button className="btn btn-outline-primary" onClick={onPrint}>
            <i className="fas fa-print"></i> Print Recipe
          </button>
        </div>
      </div>
    </div>
  );
};

export default RecipeHeader;