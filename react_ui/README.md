# Tesoro Boricua - React UI

React version of the Tesoro Boricua Cultural Learning Platform, focusing on core functionality from the Shiny app.

## Features

### 🏠 Landing Page
- Welcome section with platform introduction
- Navigation tiles for available sections
- Clean, responsive design inspired by the original Shiny app

### 📖 Language & Words
- Search Puerto Rican Spanish terms and phrases
- Filter by source (Tesoro dictionary, Dialecto cultural content)
- Multiple search types: partial match, exact term, definition search
- Bilingual definitions (Spanish and English)
- Source attribution and overlap indicators

### 🗺️ Discover Puerto Rico
- Browse Puerto Rico attractions and tourist sites
- Filter by category, city, and rating
- Detailed attraction information with highlights
- Links to TripAdvisor for more details

## Getting Started

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn

### Installation

1. Navigate to the react_ui directory:
```bash
cd react_ui
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Open [http://localhost:3000](http://localhost:3000) to view the app in your browser.

## Project Structure

```
react_ui/
├── public/
│   └── index.html          # HTML template with Font Awesome icons
├── src/
│   ├── components/
│   │   └── Header.js       # App header component
│   ├── pages/
│   │   ├── LandingPage.js  # Home page with navigation tiles
│   │   ├── LanguagePage.js # Language learning functionality
│   │   └── DiscoverPage.js # Puerto Rico attractions
│   ├── styles/
│   │   └── App.css         # Main stylesheet with responsive design
│   ├── App.js              # Main app component with routing
│   └── index.js            # App entry point
├── package.json            # Dependencies and scripts
└── README.md              # This file
```

## Differences from Shiny App

This React version includes only the core functionality requested:

**Included:**
- ✅ Landing page with navigation tiles
- ✅ Language & Words section with search
- ✅ Discover Puerto Rico section

**Not Included (as requested):**
- ❌ Music & Arts section
- ❌ History & Culture section
- ❌ Meet the Community section
- ❌ Food & Recipes section
- ❌ Complex learning modes
- ❌ Statistical visualizations

## Data Integration

Currently uses mock data for demonstration. To integrate with real data:

1. **Language Data**: Load JSON files from `../data/translated/` directories
2. **Attractions Data**: Load from `../data/preprocessed/preprocessed_discover/puerto_rico_attractions_processed.json`

## Styling

- Uses CSS Grid and Flexbox for responsive layouts
- Font Awesome icons for visual elements
- Color scheme matching the original Shiny app
- Mobile-first responsive design
- Smooth transitions and hover effects

## Available Scripts

- `npm start` - Run development server
- `npm build` - Build for production
- `npm test` - Run test suite
- `npm eject` - Eject from Create React App (irreversible)

## Browser Support

Modern browsers with ES6+ support:
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+