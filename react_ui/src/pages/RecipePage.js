import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { recipeList, getRecipesByCategory, searchRecipes } from '../data/recipeProcessor';

const RecipePage = () => {
  const navigate = useNavigate();
  const [recipes, setRecipes] = useState(recipeList);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(false);

  const categories = [
    { value: 'all', label: 'All Recipes', labelSpanish: 'Todas las Recetas' },
    { value: 'Main Dish', label: 'Main Dishes', labelSpanish: 'Platos Principales' },
    { value: 'Side Dish', label: 'Side Dishes', labelSpanish: 'Acompañantes' },
    { value: 'Appetizer', label: 'Appetizers', labelSpanish: 'Aperitivos' },
    { value: 'Beverage', label: 'Beverages', labelSpanish: 'Bebidas' },
    { value: 'Condiment', label: 'Condiments', labelSpanish: 'Condimentos' }
  ];

  const handleSearch = () => {
    setLoading(true);
    let filteredRecipes = recipeList;

    // Apply search filter
    if (searchQuery.trim()) {
      filteredRecipes = searchRecipes(searchQuery);
    }

    // Apply category filter
    if (selectedCategory !== 'all') {
      filteredRecipes = filteredRecipes.filter(recipe =>
        recipe.category === selectedCategory
      );
    }

    setRecipes(filteredRecipes);
    setLoading(false);
  };

  const handleClear = () => {
    setSearchQuery('');
    setSelectedCategory('all');
    setRecipes(recipeList);
  };

  const handleRecipeClick = (recipeId) => {
    navigate(`/recipes/${recipeId}`);
  };

  useEffect(() => {
    handleSearch();
  }, [selectedCategory]);

  const getDifficultyColor = (difficulty) => {
    switch (difficulty.toLowerCase()) {
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
    <div className="container">
      <Link to="/" className="back-button">
        <i className="fas fa-arrow-left"></i> Back to Home
      </Link>

      <div className="page-content">
        <div className="page-header">
          <h2>🇵🇷 Puerto Rican Recipes</h2>
          <p>Discover authentic Puerto Rican recipes passed down through generations. From traditional holiday dishes to everyday favorites.</p>
        </div>

        {/* Search and Filter Section */}
        <div className="search-section">
          <div className="search-form">
            <input
              type="text"
              className="search-input"
              placeholder="Search recipes... e.g., 'pernil', 'arroz', 'coquito'"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>

          <div className="search-filters">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              {categories.map(category => (
                <option key={category.value} value={category.value}>
                  {category.label}
                </option>
              ))}
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
        {recipes.length > 0 && (
          <div className="results-summary">
            <strong>Found {recipes.length} {recipes.length === 1 ? 'recipe' : 'recipes'}</strong>
            {searchQuery && ` for "${searchQuery}"`}
            {selectedCategory !== 'all' && ` in ${selectedCategory}`}
            <div className="results-hint">
              💡 Click on any recipe to see the full instructions and ingredients
            </div>
          </div>
        )}

        {/* Recipe Grid */}
        <div className="recipe-grid">
          {loading ? (
            <div className="loading-message">
              <h3>🔄 Loading recipes...</h3>
              <p>Please wait while we fetch the recipes.</p>
            </div>
          ) : recipes.length === 0 ? (
            <div className="no-results">
              <h3>🔍 No recipes found</h3>
              <p>Try adjusting your search query or category filter.</p>
            </div>
          ) : (
            recipes.map((recipe) => (
              <div
                key={recipe.id}
                className="recipe-card"
                onClick={() => handleRecipeClick(recipe.id)}
              >
                <div className="recipe-image">
                  <img
                    src={recipe.image}
                    alt={recipe.name}
                    onError={(e) => {
                      e.target.src = '/recipes/images/default-recipe.jpg';
                    }}
                  />
                  <div className="recipe-category">
                    {getCategoryIcon(recipe.category)} {recipe.category}
                  </div>
                </div>

                <div className="recipe-content">
                  <div className="recipe-header">
                    <h3>{recipe.name}</h3>
                    <div className="recipe-meta">
                      <span
                        className="difficulty-badge"
                        style={{ backgroundColor: getDifficultyColor(recipe.difficulty) }}
                      >
                        {recipe.difficulty}
                      </span>
                    </div>
                  </div>

                  <p className="recipe-description">{recipe.description}</p>

                  <div className="recipe-details">
                    <div className="recipe-detail">
                      <i className="fas fa-clock"></i>
                      <span>{recipe.cookingTime}</span>
                    </div>
                    <div className="recipe-detail">
                      <i className="fas fa-users"></i>
                      <span>{recipe.servings} servings</span>
                    </div>
                  </div>

                  <div className="recipe-footer">
                    <span className="recipe-action">
                      View Recipe <i className="fas fa-arrow-right"></i>
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Info Section */}
        <div className="recipe-info">
          <h4>🏠 About Our Recipes</h4>
          <p>
            These recipes have been carefully collected and tested to bring you authentic Puerto Rican flavors.
            Each recipe includes traditional preparation methods and ingredients that you can find in most grocery stores.
            Some recipes may include optional ingredients or variations to suit different tastes and dietary needs.
          </p>
          <p>
            <strong>Tip:</strong> Many of these recipes taste even better the next day as the flavors have time to meld together!
          </p>
        </div>
      </div>
    </div>
  );
};

export default RecipePage;