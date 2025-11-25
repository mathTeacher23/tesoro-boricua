import React, { useState } from 'react';

// Configuration object for easy size updates
const RECIPE_CONTENT_CONFIG = {
  padding: '2rem',
  minHeight: '200px',
  maxHeight: '90vh',
  tabPadding: '1rem 1.5rem',
  contentPadding: '2rem',
  contentMinHeight: '500px',
  borderRadius: '12px',
  gap: '1.5rem',
  maxContentWidth: '100%',
};

const styles = {
  container: {
    background: '#fff',
    borderRadius: RECIPE_CONTENT_CONFIG.borderRadius,
    boxShadow: '0 4px 15px rgba(0,0,0,0.1)',
    overflow: 'hidden',
    marginBottom: '2rem',
    minHeight: RECIPE_CONTENT_CONFIG.minHeight,
    boxSizing: 'border-box' as const,
    border: 'none',
    display: 'flex',
    flexDirection: 'column' as const,
  },
  tabsContainer: {
    display: 'flex',
    background: '#f8f9fa',
    borderBottom: '1px solid #e9ecef',
    flexWrap: 'wrap' as const,
  },
  tabButton: {
    background: 'none',
    border: 'none',
    padding: RECIPE_CONTENT_CONFIG.tabPadding,
    fontSize: '0.9rem',
    fontWeight: 500,
    color: '#6c757d',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    borderBottom: '3px solid transparent',
  },
  tabButtonActive: {
    color: '#007bff',
    background: '#fff',
    borderBottomColor: '#007bff',
  },
  tabIcon: {
    marginRight: '0.5rem',
  },
  contentWrapper: {
    padding: RECIPE_CONTENT_CONFIG.contentPadding,
    minHeight: RECIPE_CONTENT_CONFIG.contentMinHeight,
    maxHeight: RECIPE_CONTENT_CONFIG.maxHeight,
    overflowY: 'auto' as const,
    overflowX: 'hidden' as const,
    width: '100%',
    boxSizing: 'border-box' as const,
    flex: 1,
  },
  section: {
    width: '100%',
    boxSizing: 'border-box' as const,
  },
  sectionTitle: {
    marginBottom: '1.5rem',
    color: '#2c3e50',
    fontSize: '1.3rem',
    fontWeight: 600,
  },
  listContainer: {
    width: '100%',
    boxSizing: 'border-box' as const,
  },
  loadingContent: {
    padding: '2rem',
    textAlign: 'center' as const,
    color: '#6c757d',
  },
};

// Ingredient Item Component
const IngredientItem: React.FC<{ ingredient: string }> = ({ ingredient }) => (
  <div
    style={{
      display: 'flex',
      alignItems: 'flex-start',
      gap: '0.75rem',
      padding: '1rem',
      background: '#f8f9fa',
      borderRadius: '8px',
      transition: 'background-color 0.2s ease',
      wordWrap: 'break-word',
      boxSizing: 'border-box' as const,
    }}
    onMouseEnter={(e) => (e.currentTarget.style.background = '#e9ecef')}
    onMouseLeave={(e) => (e.currentTarget.style.background = '#f8f9fa')}
  >
    <i
      className="fas fa-check"
      style={{
        color: '#28a745',
        fontSize: '0.9rem',
        marginTop: '0.2rem',
        flexShrink: 0,
      }}
    />
    <span
      style={{
        flex: 1,
        lineHeight: 1.5,
        fontSize: '0.95rem',
      }}
    >
      {ingredient}
    </span>
  </div>
);

// Ingredients Section Component
const IngredientsSection: React.FC<{ ingredients: string[] }> = ({ ingredients }) => (
  <div style={styles.section}>
    <h3 style={styles.sectionTitle}>🛒 Ingredients</h3>
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '1.5rem',
        width: '100%',
        boxSizing: 'border-box' as const,
      }}
    >
      {ingredients.map((ingredient, index) => (
        <IngredientItem key={index} ingredient={ingredient} />
      ))}
    </div>
  </div>
);

// Instruction Item Component
const InstructionItem: React.FC<{ index: number; instruction: string }> = ({ index, instruction }) => (
  <div
    style={{
      display: 'flex',
      gap: '1.5rem',
      alignItems: 'flex-start',
      width: '100%',
      padding: '1.5rem',
      background: '#f8f9fa',
      borderRadius: '8px',
      borderLeft: '4px solid #007bff',
      boxSizing: 'border-box' as const,
    }}
  >
    <div
      style={{
        background: '#007bff',
        color: '#fff',
        width: '32px',
        height: '32px',
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 600,
        fontSize: '0.9rem',
        flexShrink: 0,
      }}
    >
      {index + 1}
    </div>
    <div
      style={{
        flex: 1,
        lineHeight: 1.7,
        color: '#495057',
        paddingTop: '0.25rem',
        fontSize: '1rem',
      }}
    >
      {instruction.replace(/^\d+\.\s*/, '')}
    </div>
  </div>
);

// Instructions Section Component
const InstructionsSection: React.FC<{ instructions: string[] }> = ({ instructions }) => (
  <div style={styles.section}>
    <h3 style={styles.sectionTitle}>👩‍🍳 Instructions</h3>
    <div
      style={{
        display: 'flex',
        flexDirection: 'column' as const,
        gap: '2rem',
        width: '100%',
        boxSizing: 'border-box' as const,
      }}
    >
      {instructions.map((instruction, index) => (
        <InstructionItem key={index} index={index} instruction={instruction} />
      ))}
    </div>
  </div>
);

// Notes Section Component
const NotesSection: React.FC<{ notes: string[] }> = ({ notes }) => (
  <div style={styles.section}>
    <h3 style={styles.sectionTitle}>📝 Notes</h3>
    <div
      style={{
        background: '#fff3cd',
        border: '1px solid #ffeaa7',
        borderRadius: '8px',
        padding: '1.5rem',
        color: '#856404',
        boxSizing: 'border-box' as const,
      }}
    >
      {notes.map((note, index) => (
        <p key={index} style={{ margin: index === notes.length - 1 ? '0' : '0.75rem 0' }}>
          {note}
        </p>
      ))}
    </div>
  </div>
);

// Lesson Item Component
const LessonItem: React.FC<{ lesson: string }> = ({ lesson }) => (
  <div
    style={{
      display: 'flex',
      alignItems: 'flex-start',
      gap: '0.75rem',
      padding: '1rem',
      background: '#d1ecf1',
      border: '1px solid #bee5eb',
      borderRadius: '6px',
      boxSizing: 'border-box' as const,
    }}
  >
    <i
      className="fas fa-lightbulb"
      style={{
        color: '#0c5460',
        marginTop: '0.125rem',
        flexShrink: 0,
      }}
    />
    <span style={{ color: '#0c5460' }}>{lesson}</span>
  </div>
);

// Lessons Section Component
const LessonsSection: React.FC<{ lessons: string[] }> = ({ lessons }) => (
  <div style={styles.section}>
    <h3 style={styles.sectionTitle}>💡 Lessons Learned & Tips</h3>
    <div
      style={{
        display: 'flex',
        flexDirection: 'column' as const,
        gap: '1rem',
        width: '100%',
        boxSizing: 'border-box' as const,
      }}
    >
      {lessons.map((lesson, index) => (
        <LessonItem key={index} lesson={lesson} />
      ))}
    </div>
  </div>
);

// Main RecipeContent Component
interface RecipeContentProps {
  recipeDetails: {
    ingredients: string[];
    instructions: string[];
    notes?: string[];
    lessonsLearned?: string[];
  } | null;
  containerStyle?: React.CSSProperties;
  contentStyle?: React.CSSProperties;
}

const RecipeContent: React.FC<RecipeContentProps> = ({ recipeDetails, containerStyle = {}, contentStyle = {} }) => {
  const [activeTab, setActiveTab] = useState<'ingredients' | 'instructions' | 'notes' | 'lessons'>('ingredients');

  if (!recipeDetails) {
    return (
      <div style={{ ...styles.container, ...containerStyle }}>
        <div style={styles.loadingContent}>
          <p>Loading recipe details...</p>
        </div>
      </div>
    );
  }

  const tabButtons = [
    { id: 'ingredients', label: 'Ingredients', icon: 'fas fa-list' },
    { id: 'instructions', label: 'Instructions', icon: 'fas fa-tasks' },
    ...(recipeDetails.notes && recipeDetails.notes.length > 0
      ? [{ id: 'notes', label: 'Notes', icon: 'fas fa-sticky-note' }]
      : []),
    ...(recipeDetails.lessonsLearned && recipeDetails.lessonsLearned.length > 0
      ? [{ id: 'lessons', label: 'Tips', icon: 'fas fa-lightbulb' }]
      : []),
  ] as Array<{ id: 'ingredients' | 'instructions' | 'notes' | 'lessons'; label: string; icon: string }>;

  return (
    <div style={{ ...styles.container, ...containerStyle }}>
      {/* Tabs */}
      <div style={styles.tabsContainer}>
        {tabButtons.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              ...styles.tabButton,
              ...(activeTab === tab.id ? styles.tabButtonActive : {}),
            }}
            onMouseEnter={(e) => {
              if (activeTab !== tab.id) {
                e.currentTarget.style.background = '#e9ecef';
                e.currentTarget.style.color = '#495057';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== tab.id) {
                e.currentTarget.style.background = 'none';
                e.currentTarget.style.color = '#6c757d';
              }
            }}
          >
            <i className={tab.icon} style={styles.tabIcon} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div style={{ ...styles.contentWrapper, ...contentStyle }}>
        {activeTab === 'ingredients' && <IngredientsSection ingredients={recipeDetails.ingredients} />}
        {activeTab === 'instructions' && <InstructionsSection instructions={recipeDetails.instructions} />}
        {activeTab === 'notes' && recipeDetails.notes && <NotesSection notes={recipeDetails.notes} />}
        {activeTab === 'lessons' && recipeDetails.lessonsLearned && <LessonsSection lessons={recipeDetails.lessonsLearned} />}
      </div>
    </div>
  );
};

export default RecipeContent;
