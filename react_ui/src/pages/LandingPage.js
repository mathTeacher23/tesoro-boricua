import React from 'react';
import { useNavigate } from 'react-router-dom';

const LandingPage = () => {
  const navigate = useNavigate();

  const handleLanguageClick = () => {
    navigate('/language');
  };

  const handleDiscoverClick = () => {
    navigate('/discover');
  };

  const handleRecipesClick = () => {
    navigate('/recipes');
  };

  return (
    <div className="container">
      {/* Welcome Section */}
      <div className="welcome-section">
        <h1>🇵🇷 ¡Bienvenidos a Tesoro Boricua!</h1>
        <h2>Welcome to your Puerto Rican Cultural Learning Platform</h2>
        <p>Reconnect with your roots through language, food, music, and history.</p>
      </div>

      {/* Navigation Tiles */}
      <div className="tiles-grid">
        {/* Language & Words Tile */}
        <div className="tile available" onClick={handleLanguageClick}>
          <div>
            <div className="tile-icon language">
              <i className="fas fa-language"></i>
            </div>
            <h4>📖 Language & Words</h4>
            <p>Explore Puerto Rican Spanish words, phrases, and expressions.</p>
            <div className="tile-badges">
              <span className="badge success">2,500+ entries</span>
              <span className="badge info">Available Now</span>
            </div>
          </div>
          <button className="btn btn-success">Start Learning</button>
        </div>

        {/* Discover Puerto Rico Tile */}
        <div className="tile available" onClick={handleDiscoverClick}>
          <div>
            <div className="tile-icon discover">
              <i className="fas fa-map-marked-alt"></i>
            </div>
            <h4>🗺️ Discover Puerto Rico</h4>
            <p>Plan your journey to the island! Explore tourist sites and create itineraries.</p>
            <div className="tile-badges">
              <span className="badge success">20 attractions</span>
              <span className="badge info">Available Now</span>
            </div>
          </div>
          <button className="btn btn-info">Explore Attractions</button>
        </div>

        {/* Puerto Rican Recipes Tile */}
        <div className="tile available" onClick={handleRecipesClick}>
          <div>
            <div className="tile-icon recipes">
              <i className="fas fa-utensils"></i>
            </div>
            <h4>🍽️ Puerto Rican Recipes</h4>
            <p>Discover authentic Puerto Rican recipes passed down through generations.</p>
            <div className="tile-badges">
              <span className="badge success">6 recipes</span>
              <span className="badge info">Available Now</span>
            </div>
          </div>
          <button className="btn btn-success">View Recipes</button>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;