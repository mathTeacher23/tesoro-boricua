import React from 'react';

// Configuration object for easy updates
const RECIPE_HEADER_CONFIG = {
  imageWidth: '300px',
  imageHeight: '200px',
  gap: '2rem',
  padding: '2rem',
  borderRadius: '12px',
};

const styles = {
  container: {
    display: 'grid',
    gridTemplateColumns: `${RECIPE_HEADER_CONFIG.imageWidth} 1fr`,
    gap: RECIPE_HEADER_CONFIG.gap,
    marginBottom: '2rem',
    background: '#fff',
    borderRadius: RECIPE_HEADER_CONFIG.borderRadius,
    padding: RECIPE_HEADER_CONFIG.padding,
    boxShadow: '0 4px 15px rgba(0,0,0,0.1)',
    boxSizing: 'border-box' as const,
    border: 'none',
  },
  imageSection: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  image: {
    width: '100%',
    height: RECIPE_HEADER_CONFIG.imageHeight,
    objectFit: 'cover' as const,
    borderRadius: '8px',
  },
  infoSection: {
    display: 'flex',
    flexDirection: 'column' as const,
    justifyContent: 'flex-start',
  },
  categoryTag: {
    display: 'inline-block',
    background: '#e3f2fd',
    color: '#1976d2',
    padding: '0.5rem 1rem',
    borderRadius: '20px',
    fontSize: '0.8rem',
    fontWeight: 500,
    marginBottom: '1rem',
    width: 'fit-content',
  },
  title: {
    fontSize: '2.5rem',
    color: '#2c3e50',
    marginBottom: '1rem',
    fontWeight: 700,
    margin: '0 0 1rem 0',
  },
  description: {
    fontSize: '1.1rem',
    color: '#6c757d',
    lineHeight: 1.6,
    marginBottom: '2rem',
    margin: '0 0 2rem 0',
  },
  metaContainer: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
    gap: '1rem',
    marginBottom: '2rem',
  },
  metaItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    padding: '1rem',
    background: '#f8f9fa',
    borderRadius: '8px',
    boxSizing: 'border-box' as const,
  },
  metaIcon: {
    fontSize: '1.2rem',
    color: '#007bff',
  },
  metaContent: {
    display: 'flex',
    flexDirection: 'column' as const,
  },
  metaLabel: {
    fontSize: '0.8rem',
    color: '#6c757d',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
    fontWeight: 500,
    margin: 0,
  },
  metaValue: {
    fontWeight: 500,
    color: '#2c3e50',
  },
  difficultyBadge: {
    color: '#fff',
    padding: '0.25rem 0.75rem',
    borderRadius: '15px',
    fontSize: '0.7rem',
    fontWeight: 500,
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
    display: 'inline-block',
    width: 'fit-content',
  },
  actionsContainer: {
    display: 'flex',
    gap: '1rem',
  },
  printButton: {
    background: '#007bff',
    color: '#fff',
    border: '1px solid #007bff',
    padding: '0.75rem 1.5rem',
    borderRadius: '6px',
    fontSize: '0.9rem',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    textDecoration: 'none',
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
};

// Meta Item Component
interface MetaItemProps {
  icon: string;
  label: string;
  value: string;
}

const MetaItem: React.FC<MetaItemProps> = ({ icon, label, value }) => (
  <div style={styles.metaItem}>
    <i className={icon} style={styles.metaIcon} />
    <div style={styles.metaContent}>
      <strong style={styles.metaLabel}>{label}</strong>
      <span style={styles.metaValue}>{value}</span>
    </div>
  </div>
);

// Main RecipeHeader Component
interface RecipeHeaderProps {
  recipe: {
    image: string;
    name: string;
    category: string;
    description: string;
    cookingTime: string;
    servings: string;
    difficulty: string;
  };
  onPrint: () => void;
  containerStyle?: React.CSSProperties;
}

const RecipeHeader: React.FC<RecipeHeaderProps> = ({ recipe, onPrint, containerStyle = {} }) => {
  const getDifficultyColor = (difficulty: string): string => {
    const normalized = difficulty?.toLowerCase();
    switch (normalized) {
      case 'easy':
        return '#28a745';
      case 'medium':
        return '#ffc107';
      case 'hard':
        return '#dc3545';
      default:
        return '#6c757d';
    }
  };

  const getCategoryIcon = (category: string): string => {
    switch (category) {
      case 'Main Dish':
        return '🍽️';
      case 'Side Dish':
        return '🥘';
      case 'Appetizer':
        return '🥟';
      case 'Beverage':
        return '🥤';
      case 'Condiment':
        return '🧄';
      default:
        return '🍴';
    }
  };

  return (
    <div style={{ ...styles.container, ...containerStyle }}>
      {/* Image Section */}
      <div style={styles.imageSection}>
        <img
          src={recipe.image}
          alt={recipe.name}
          style={styles.image}
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = '/recipes/images/default-recipe.jpg';
          }}
        />
      </div>

      {/* Info Section */}
      <div style={styles.infoSection}>
        <div style={styles.categoryTag}>
          {getCategoryIcon(recipe.category)} {recipe.category}
        </div>

        <h1 style={styles.title}>{recipe.name}</h1>
        <p style={styles.description}>{recipe.description}</p>

        {/* Meta Information */}
        <div style={styles.metaContainer}>
          <MetaItem icon="fas fa-clock" label="Cooking Time" value={recipe.cookingTime} />
          <MetaItem icon="fas fa-users" label="Servings" value={recipe.servings} />
          <div style={styles.metaItem}>
            <i className="fas fa-signal" style={styles.metaIcon} />
            <div style={styles.metaContent}>
              <strong style={styles.metaLabel}>Difficulty</strong>
              <span
                style={{
                  ...styles.difficultyBadge,
                  backgroundColor: getDifficultyColor(recipe.difficulty),
                }}
              >
                {recipe.difficulty}
              </span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div style={styles.actionsContainer}>
          <button
            style={styles.printButton}
            onClick={onPrint}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#0056b3';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#007bff';
            }}
          >
            <i className="fas fa-print" /> Print Recipe
          </button>
        </div>
      </div>
    </div>
  );
};

export default RecipeHeader;
