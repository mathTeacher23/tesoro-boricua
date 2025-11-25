import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { getRecipeById, parseRecipeMarkdown } from '../data/recipeProcessor';
import RecipeHeader from '../components/RecipeHeader.tsx';
import RecipeContent from '../components/RecipeContent.tsx';

const RecipeDetailPage = () => {
  const { recipeId } = useParams();
  const navigate = useNavigate();
  const [recipe, setRecipe] = useState(null);
  const [recipeDetails, setRecipeDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showTooltip, setShowTooltip] = useState(false);

  useEffect(() => {
    const loadRecipe = async () => {
      setLoading(true);
      setError(null);

      // Get basic recipe info
      const basicRecipe = getRecipeById(recipeId);
      if (!basicRecipe) {
        setError('Recipe not found');
        setLoading(false);
        return;
      }

      setRecipe(basicRecipe);

      // Parse detailed recipe content from markdown
      try {
        const details = await parseRecipeMarkdown(recipeId);
        if (details) {
          setRecipeDetails(details);
        } else {
          setError('Could not load recipe details');
        }
      } catch (err) {
        console.error('Error loading recipe details:', err);
        setError('Could not load recipe details');
      }

      setLoading(false);
    };

    if (recipeId) {
      loadRecipe();
    }
  }, [recipeId]);


  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading-message">
          <h3>🔄 Loading recipe...</h3>
          <p>Please wait while we fetch the recipe details.</p>
        </div>
      </div>
    );
  }

  if (error || !recipe) {
    return (
      <div className="container">
        <Link to="/recipes" className="back-button">
          <i className="fas fa-arrow-left"></i> Back to Recipes
        </Link>
        <div className="error-message">
          <h3>❌ {error || 'Recipe not found'}</h3>
          <p>The recipe you're looking for doesn't exist or couldn't be loaded.</p>
          <button className="btn btn-primary" onClick={() => navigate('/recipes')}>
            Browse All Recipes
          </button>
        </div>
      </div>
    );
  }

  // Define unified container styles with full width
  const pageWrapperStyle = {
    width: '100vw',
    marginLeft: 'calc(-50vw + 50%)',
    display: 'flex',
    flexDirection: 'column',
    gap: '0'
  };

  const headerBarStyle = {
    background: '#fff',
    padding: '1rem 2rem',
    borderBottom: '1px solid #e9ecef',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    width: '100%',
    boxSizing: 'border-box'
  };

  const recipePageContainerStyle = {
    maxWidth: '100%',
    margin: '0 auto',
    padding: '2rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '2rem',
    boxSizing: 'border-box',
    width: '100%'
  };

  const recipeHeaderContainerStyle = {
    width: '100%',
    margin: '0 auto',
    maxWidth: 'none'
  };

  const recipeContentContainerStyle = {
    width: '100%',
    margin: '0 auto',
    maxWidth: 'none'
  };

  const shareButtonStyle = {
    position: 'relative',
    display: 'inline-block'
  };

  const tooltipStyle = {
    visibility: 'hidden',
    backgroundColor: '#333',
    color: '#fff',
    textAlign: 'center',
    borderRadius: '6px',
    padding: '0.75rem 1rem',
    position: 'absolute',
    zIndex: 1,
    bottom: '125%',
    left: '50%',
    marginLeft: '-75px',
    opacity: 0,
    transition: 'opacity 0.3s',
    whiteSpace: 'nowrap',
    fontSize: '0.85rem',
    width: '150px'
  };

  return (
    <div style={pageWrapperStyle}>
      {/* Top Header Bar with Back Button */}
      <div style={headerBarStyle}>
        <Link to="/recipes" className="back-button" style={{ marginBottom: 0 }}>
          <i className="fas fa-arrow-left"></i> Back to Recipes
        </Link>

        {/* Share Button with Tooltip */}
        <div
          style={shareButtonStyle}
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
        >
          <button
            style={{
              background: '#007bff',
              color: '#fff',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.9rem',
              fontWeight: 500,
              transition: 'background-color 0.3s',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#0056b3')}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#007bff')}
          >
            <i className="fas fa-share-alt"></i> Share
          </button>
          <div
            style={{
              ...tooltipStyle,
              visibility: showTooltip ? 'visible' : 'hidden',
              opacity: showTooltip ? 1 : 0
            }}
          >
            🫶 Love this recipe? Share it with family and friends to spread the delicious Puerto Rican tradition!
          </div>
        </div>
      </div>

      {/* Main Recipe Container */}
      <div style={recipePageContainerStyle}>
        {/* Recipe Header Component */}
        <RecipeHeader
          recipe={recipe}
          onPrint={handlePrint}
          containerStyle={recipeHeaderContainerStyle}
        />

        {/* Recipe Content Component */}
        <RecipeContent
          recipeDetails={recipeDetails}
          containerStyle={recipeContentContainerStyle}
        />
      </div>

      {/* YouTube Video Placeholder - Ready for future implementation */}
      <div className="video-section" style={{ display: 'none' }}>
        <h3>🎥 Video Tutorial</h3>
        <div className="video-placeholder">
          <p>Video content will be available soon!</p>
        </div>
      </div>
    </div>
  );
};

export default RecipeDetailPage;