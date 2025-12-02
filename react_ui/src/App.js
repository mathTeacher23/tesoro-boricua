import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import LandingPage from './pages/LandingPage';
import LanguagePage from './pages/LanguagePage';
import DiscoverPage from './pages/DiscoverPage';
import RecipePage from './pages/RecipePage';
import RecipeDetailPage from './pages/RecipeDetailPage';
import MusicArtsPage from './pages/MusicArtsPage';
import HistoryCulturePage from './pages/HistoryCulturePage';
import MeetCommunityPage from './pages/MeetCommunityPage';
import CreatorBioPage from './pages/CreatorBioPage';
import './styles/App.css';

function App() {
  return (
    <div className="app">
      <Router>
        <Header />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/language" element={<LanguagePage />} />
          <Route path="/language/:letter" element={<LanguagePage />} />
          <Route path="/discover" element={<DiscoverPage />} />
          <Route path="/recipes" element={<RecipePage />} />
          <Route path="/recipes/:recipeId" element={<RecipeDetailPage />} />
          <Route path="/music-arts" element={<MusicArtsPage />} />
          <Route path="/history-culture" element={<HistoryCulturePage />} />
          <Route path="/meet-community" element={<MeetCommunityPage />} />
          <Route path="/creator-bio" element={<CreatorBioPage />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;