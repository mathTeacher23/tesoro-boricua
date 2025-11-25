// Recipe data processor to parse markdown files and structure recipe data

export const recipeList = [
  {
    id: 'pernil',
    name: 'Pernil',
    nameSpanish: 'Pernil',
    description: 'Traditional Puerto Rican roasted pork shoulder, seasoned and slow-cooked to perfection',
    descriptionSpanish: 'Cerdo asado tradicional puertorriqueño, sazonado y cocido lentamente a la perfección',
    category: 'Main Dish',
    categorySpanish: 'Plato Principal',
    cookingTime: '5-6 hours',
    servings: '8-10',
    difficulty: 'Medium',
    image: '/recipes/images/pernil.jpeg'
  },
  {
    id: 'arrozcongandules',
    name: 'Arroz con Gandules',
    nameSpanish: 'Arroz con Gandules',
    description: 'The national dish of Puerto Rico - rice with pigeon peas, sofrito, and savory seasonings',
    descriptionSpanish: 'El plato nacional de Puerto Rico - arroz con gandules, sofrito y sazonadores sabrosos',
    category: 'Side Dish',
    categorySpanish: 'Acompañante',
    cookingTime: '45 minutes',
    servings: '6-8',
    difficulty: 'Easy',
    image: '/recipes/images/arrozcongandules.jpeg'
  },
  {
    id: 'coquito',
    name: 'Coquito',
    nameSpanish: 'Coquito',
    description: 'Puerto Rican eggnog - a creamy, coconut-based holiday drink with rum and warm spices',
    descriptionSpanish: 'Ponche puertorriqueño - una bebida navideña cremosa a base de coco con ron y especias',
    category: 'Beverage',
    categorySpanish: 'Bebida',
    cookingTime: '15 minutes',
    servings: '8-10',
    difficulty: 'Easy',
    image: '/recipes/images/coquito.jpeg'
  },
  {
    id: 'pastelillos',
    name: 'Pastelillos',
    nameSpanish: 'Pastelillos',
    description: 'Crispy fried turnovers filled with seasoned meat, cheese, or other savory fillings',
    descriptionSpanish: 'Empanadas fritas crujientes rellenas de carne sazonada, queso u otros rellenos sabrosos',
    category: 'Appetizer',
    categorySpanish: 'Aperitivo',
    cookingTime: '1 hour',
    servings: '12-15',
    difficulty: 'Medium',
    image: '/recipes/images/pastelillos.jpeg'
  },
  {
    id: 'carnemechada',
    name: 'Carne Mechada',
    nameSpanish: 'Carne Mechada',
    description: 'Shredded beef in a rich tomato-based sauce, perfect for filling empanadas or serving over rice',
    descriptionSpanish: 'Carne deshebrada en salsa rica de tomate, perfecta para rellenar empanadas o servir sobre arroz',
    category: 'Main Dish',
    categorySpanish: 'Plato Principal',
    cookingTime: '2-3 hours',
    servings: '6-8',
    difficulty: 'Medium',
    image: '/recipes/images/carnemechada.jpeg'
  },
  {
    id: 'sofrito',
    name: 'Sofrito',
    nameSpanish: 'Sofrito',
    description: 'The foundation of Puerto Rican cuisine - a flavorful base made with peppers, onions, garlic, and herbs',
    descriptionSpanish: 'La base de la cocina puertorriqueña - una base sabrosa hecha con pimientos, cebollas, ajo y hierbas',
    category: 'Condiment',
    categorySpanish: 'Condimento',
    cookingTime: '30 minutes',
    servings: '20+ portions',
    difficulty: 'Easy',
    image: '/recipes/images/sofrito.jpg'
  }
];

export const parseRecipeMarkdown = async (recipeId) => {
  try {
    const response = await fetch(`/recipes/${recipeId}.md`);
    if (!response.ok) {
      throw new Error(`Failed to fetch recipe: ${recipeId}`);
    }

    const text = await response.text();
    const lines = text.split('\n');

    let ingredients = [];
    let instructions = [];
    let notes = [];
    let lessonsLearned = [];

    let currentSection = null;

    for (let line of lines) {
      line = line.trim();

      if (line.toLowerCase().startsWith('ingredients:')) {
        currentSection = 'ingredients';
        continue;
      } else if (line.toLowerCase().startsWith('instructions:')) {
        currentSection = 'instructions';
        continue;
      } else if (line.toLowerCase().startsWith('note:')) {
        currentSection = 'notes';
        continue;
      } else if (line.toLowerCase().startsWith('lessons learned:')) {
        currentSection = 'lessonsLearned';
        continue;
      }

      if (line === '') {
        continue;
      }

      switch (currentSection) {
        case 'ingredients':
          if (line.startsWith('* ')) {
            ingredients.push(line.substring(2));
          }
          break;
        case 'instructions':
          if (line.match(/^\d+\./)) {
            instructions.push(line);
          } else if (instructions.length > 0 && line.trim() !== '') {
            // Continue previous instruction if it's a continuation line
            instructions[instructions.length - 1] += ' ' + line;
          }
          break;
        case 'notes':
          if (line && !line.toLowerCase().startsWith('note:')) {
            notes.push(line);
          }
          break;
        case 'lessonsLearned':
          if (line.startsWith('* ')) {
            lessonsLearned.push(line.substring(2));
          }
          break;
      }
    }

    console.log('Recipe parsing result:', {
      recipeId,
      ingredients: ingredients.length,
      instructions: instructions.length,
      notes: notes.length,
      lessonsLearned: lessonsLearned.length,
      instructionsData: instructions
    });

    return {
      ingredients,
      instructions,
      notes,
      lessonsLearned
    };

  } catch (error) {
    console.error('Error parsing recipe markdown:', error);
    return null;
  }
};

export const getRecipeById = (recipeId) => {
  return recipeList.find(recipe => recipe.id === recipeId);
};

export const getRecipesByCategory = (category) => {
  if (!category || category === 'all') return recipeList;
  return recipeList.filter(recipe =>
    recipe.category.toLowerCase() === category.toLowerCase()
  );
};

export const searchRecipes = (query) => {
  if (!query) return recipeList;

  const lowercaseQuery = query.toLowerCase();
  return recipeList.filter(recipe =>
    recipe.name.toLowerCase().includes(lowercaseQuery) ||
    recipe.nameSpanish.toLowerCase().includes(lowercaseQuery) ||
    recipe.description.toLowerCase().includes(lowercaseQuery) ||
    recipe.descriptionSpanish.toLowerCase().includes(lowercaseQuery)
  );
};