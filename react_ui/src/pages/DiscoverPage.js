import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const DiscoverPage = () => {
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [cityFilter, setCityFilter] = useState('all');
  const [ratingFilter, setRatingFilter] = useState(0);
  const [results, setResults] = useState([]);
  const [filteredResults, setFilteredResults] = useState([]);
  const [loading, setLoading] = useState(false);

  // Mock data based on the JSON structure
  const mockAttractions = [
    {
      id: "pr_attraction_1",
      name: "Flamenco Beach",
      description: "Pristine white sand beach on Culebra island, consistently ranked among the world's most beautiful beaches. Crystal clear turquoise waters perfect for swimming and snorkeling.",
      url: "https://www.tripadvisor.com/Attraction_Review-g616348-d184059-Reviews-Flamenco_Beach-Culebra.html",
      city: "Culebra",
      rating: 5.0,
      review_count: 8234,
      category: "Beaches & Water Activities",
      highlights: [
        "Consistently ranked top 10 beach worldwide",
        "Pristine white sand and crystal clear water",
        "Excellent snorkeling with tropical fish",
        "Abandoned military tanks as unique photo ops",
        "Less crowded than mainland beaches"
      ],
      popularity_score: 260.0
    },
    {
      id: "pr_attraction_2",
      name: "El Yunque National Forest",
      description: "The only tropical rainforest in the US National Forest System. Features stunning waterfalls, hiking trails, and diverse wildlife including the famous coquí frogs.",
      url: "https://www.tripadvisor.com/Attraction_Review-g147320-d184096-Reviews-El_Yunque_National_Forest-Puerto_Rico.html",
      city: "Rio Grande",
      rating: 4.8,
      review_count: 5432,
      category: "Nature & Parks",
      highlights: [
        "Only tropical rainforest in US National Forest System",
        "Beautiful waterfalls and swimming holes",
        "Home to the iconic coquí frogs",
        "Multiple hiking trails for all levels",
        "Stunning biodiversity and bird watching"
      ],
      popularity_score: 245.0
    },
    {
      id: "pr_attraction_3",
      name: "Old San Juan",
      description: "Historic colonial district with cobblestone streets, colorful Spanish architecture, forts, museums, and vibrant culture. A UNESCO World Heritage Site.",
      url: "https://www.tripadvisor.com/Attraction_Review-g147320-d184097-Reviews-Old_San_Juan-San_Juan_Puerto_Rico.html",
      city: "San Juan",
      rating: 4.7,
      review_count: 12456,
      category: "Historic Sites",
      highlights: [
        "UNESCO World Heritage Site",
        "Beautiful Spanish colonial architecture",
        "Historic forts El Morro and San Cristóbal",
        "Colorful buildings and cobblestone streets",
        "Great restaurants, shops, and nightlife"
      ],
      popularity_score: 230.0
    },
    {
      id: "pr_attraction_4",
      name: "Mosquito Bay",
      description: "Bioluminescent bay on Vieques island where microscopic organisms create a magical glowing effect in the water at night. Best experienced on moonless nights.",
      url: "https://www.tripadvisor.com/Attraction_Review-g580415-d184098-Reviews-Mosquito_Bay-Vieques_Puerto_Rico.html",
      city: "Vieques",
      rating: 4.6,
      review_count: 3421,
      category: "Nature & Parks",
      highlights: [
        "Brightest bioluminescent bay in the world",
        "Magical glowing water phenomenon",
        "Best viewed on dark, moonless nights",
        "Kayak tours available",
        "Unique and unforgettable experience"
      ],
      popularity_score: 220.0
    },
    {
      id: "pr_attraction_5",
      name: "Camuy Caves",
      description: "One of the world's largest cave networks with spectacular limestone formations, underground rivers, and guided tours through massive chambers.",
      url: "https://www.tripadvisor.com/Attraction_Review-g580415-d184099-Reviews-Camuy_Caves-Camuy_Puerto_Rico.html",
      city: "Camuy",
      rating: 4.4,
      review_count: 2156,
      category: "Nature & Parks",
      highlights: [
        "One of world's largest cave systems",
        "Spectacular limestone formations",
        "Underground rivers and chambers",
        "Educational guided tours",
        "Cool temperatures year-round"
      ],
      popularity_score: 180.0
    }
  ];

  useEffect(() => {
    setResults(mockAttractions);
    setFilteredResults(mockAttractions);
  }, []);

  const handleFilter = () => {
    setLoading(true);

    setTimeout(() => {
      let filtered = mockAttractions;

      // Apply category filter
      if (categoryFilter !== 'all') {
        filtered = filtered.filter(attraction => attraction.category === categoryFilter);
      }

      // Apply city filter
      if (cityFilter !== 'all') {
        filtered = filtered.filter(attraction => attraction.city === cityFilter);
      }

      // Apply rating filter
      if (ratingFilter > 0) {
        filtered = filtered.filter(attraction => attraction.rating >= ratingFilter);
      }

      // Sort by popularity score
      filtered = filtered.sort((a, b) => b.popularity_score - a.popularity_score);

      setFilteredResults(filtered);
      setLoading(false);
    }, 300);
  };

  const createAttractionCard = (attraction, index) => {
    const rating_display = attraction.rating > 0
      ? `⭐ ${attraction.rating}/5.0`
      : "⭐ No rating";

    const review_count_display = attraction.review_count > 0
      ? ` (${attraction.review_count.toLocaleString()} reviews)`
      : "";

    const description_text = attraction.description.length > 300
      ? `${attraction.description.substring(0, 300)}...`
      : attraction.description;

    const highlights = attraction.highlights.slice(0, 3); // Show max 3 highlights

    return (
      <div key={index} className="attraction-card">
        <div className="attraction-header">
          <div>
            <h3 className="attraction-title">
              {attraction.name}
              <span className="attraction-category">• {attraction.category}</span>
            </h3>
          </div>
        </div>

        <div className="attraction-meta">
          <div className="location">
            <i className="fas fa-map-marker-alt"></i> {attraction.city}
          </div>
          <div className="rating">
            {rating_display}{review_count_display}
          </div>
        </div>

        <div className="attraction-description">
          {description_text}
        </div>

        {highlights.length > 0 && (
          <div className="highlights">
            <h6>Highlights:</h6>
            <ul>
              {highlights.map((highlight, idx) => (
                <li key={idx}>{highlight}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="attraction-footer">
          <a
            href={attraction.url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-outline-primary"
          >
            <i className="fas fa-external-link-alt"></i> View on TripAdvisor
          </a>
        </div>
      </div>
    );
  };

  // Get unique categories and cities for filters
  const categories = ['all', ...new Set(mockAttractions.map(a => a.category))];
  const cities = ['all', ...new Set(mockAttractions.map(a => a.city))];

  return (
    <div className="container">
      <Link to="/" className="back-button">
        <i className="fas fa-arrow-left"></i> Back to Home
      </Link>

      <div className="page-content">
        <div className="page-header">
          <h2>🗺️ Discover Puerto Rico</h2>
          <p>Plan your journey to the island! Explore tourist sites and create your perfect itinerary.</p>
        </div>

        {/* Filter Section */}
        <div className="search-section">
          <div className="search-filters">
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              <option value="all">All Categories</option>
              {categories.slice(1).map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>

            <select
              value={cityFilter}
              onChange={(e) => setCityFilter(e.target.value)}
            >
              <option value="all">All Cities</option>
              {cities.slice(1).map(city => (
                <option key={city} value={city}>{city}</option>
              ))}
            </select>

            <select
              value={ratingFilter}
              onChange={(e) => setRatingFilter(parseFloat(e.target.value))}
            >
              <option value={0}>All Ratings</option>
              <option value={4.5}>4.5+ Stars</option>
              <option value={4.0}>4.0+ Stars</option>
              <option value={3.5}>3.5+ Stars</option>
            </select>
          </div>

          <div className="search-controls">
            <button className="btn btn-info" onClick={handleFilter} disabled={loading}>
              <i className="fas fa-filter"></i> {loading ? 'Filtering...' : 'Filter Attractions'}
            </button>
          </div>
        </div>

        {/* Results Summary */}
        <div className="results-summary">
          <strong>Found {filteredResults.length} attractions</strong>
          {categoryFilter !== 'all' && ` in ${categoryFilter}`}
          {cityFilter !== 'all' && ` in ${cityFilter}`}
          {ratingFilter > 0 && ` with rating ≥ ${ratingFilter}`}
        </div>

        {/* Results Display */}
        <div className="results-container">
          {filteredResults.length === 0 ? (
            <div className="no-results">
              <h3>🗺️ No attractions found</h3>
              <p>Try adjusting your search filters.</p>
            </div>
          ) : (
            filteredResults.map((attraction, index) => createAttractionCard(attraction, index))
          )}
        </div>

        {/* Stats Summary */}
        <div className="results-summary">
          <small>
            📊 Dataset Stats: {mockAttractions.length} total attractions
            • Sourced from TripAdvisor
            • Covering {cities.length - 1} cities across Puerto Rico
          </small>
        </div>
      </div>
    </div>
  );
};

export default DiscoverPage;