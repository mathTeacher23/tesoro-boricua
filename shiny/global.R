# =============================================================================
# GLOBAL.R - Data Loading and Processing for Tesoro Boricua Cultural Platform
# =============================================================================

# Load required libraries
library(shiny)
library(shinydashboard)
library(DT)
library(jsonlite)
library(dplyr)
library(ggplot2)
library(stringr)
library(purrr)

# =============================================================================
# DATA LOADING FUNCTIONS
# =============================================================================

#' Load and combine all JSON files from a directory
#' @param directory Path to directory containing JSON files
#' @param source_name Source identifier ("Tesoro" or "Dialecto")
load_json_data <- function(directory, source_name) {
  if (!dir.exists(directory)) {
    cat(sprintf("Warning: Directory %s does not exist\n", directory))
    return(data.frame())
  }
  
  json_files <- list.files(directory, pattern = "\\.json$", full.names = TRUE)
  
  if (length(json_files) == 0) {
    cat(sprintf("Warning: No JSON files found in %s\n", directory))
    return(data.frame())
  }
  
  cat(sprintf("Loading %d files from %s\n", length(json_files), directory))
  
  # Load and combine all JSON files
  all_data <- map_dfr(json_files, function(file) {
    tryCatch({
      data <- fromJSON(file, flatten = TRUE)
      
      # Ensure consistent structure
      if (!"source" %in% names(data)) {
        data$source <- ifelse(source_name == "Tesoro", 
                             "https://tesoro.pr", 
                             "https://dialectoboricua.com")
      }
      
      # Add metadata
      data$file_source <- source_name
      data$file_name <- basename(file)
      
      return(data)
    }, error = function(e) {
      cat(sprintf("Error loading file %s: %s\n", file, e$message))
      return(data.frame())
    })
  })
  
  cat(sprintf("Loaded %d entries from %s\n", nrow(all_data), source_name))
  return(all_data)
}

#' Process and clean the combined dataset
#' @param data Raw combined data
process_data <- function(data) {
  if (nrow(data) == 0) return(data)
  
  data %>%
    # Clean term names
    mutate(
      term_clean = str_trim(term),
      term_lower = str_to_lower(term_clean),
      letter = str_to_upper(letter)
    ) %>%
    # Process definitions
    rowwise() %>%
    mutate(
      # Join definitions differently based on source
      # For Dialecto: join paragraphs with double newlines for better reading
      # For Tesoro: keep as separate definitions
      es_text_consolidated = ifelse(
        file_source == "Dialecto",
        paste(es_definitions, collapse = "\n\n"),
        paste(es_definitions, collapse = " ")
      ),
      en_text_consolidated = ifelse(
        file_source == "Dialecto", 
        paste(en_definitions, collapse = "\n\n"),
        paste(en_definitions, collapse = " ")
      ),
      
      # Count definitions
      es_def_count = length(es_definitions),
      en_def_count = length(en_definitions),
      
      # Create searchable text combining all definitions
      es_text = paste(es_definitions, collapse = " "),
      en_text = paste(en_definitions, collapse = " "),
      search_text = paste(term_clean, es_text, en_text, sep = " ")
    ) %>%
    ungroup() %>%
    # Add word statistics
    mutate(
      term_length = nchar(term_clean),
      is_phrase = str_detect(term_clean, " "),
      word_count = str_count(term_clean, "\\\\S+")
    ) %>%
    # Sort by term for better browsing
    arrange(term_clean)
}

# =============================================================================
# DATA PATHS - MODULAR STRUCTURE FOR CULTURAL SECTIONS
# =============================================================================

# Language data paths (currently available)
TESORO_PATH <- "../data/translated/translated_tesoro"
DIALECTO_PATH <- "../data/translated/translated_dialecto"

# Travel data paths (available when scraped)
DISCOVER_PATH <- "../data/preprocessed/preprocessed_discover"

# Future data paths for cultural sections (placeholders for extensibility)
# RECIPES_PATH <- "../data/food/recipes"
# MUSIC_PATH <- "../data/music/songs_and_history"  
# HISTORY_PATH <- "../data/history/events_and_culture"
# COMMUNITY_PATH <- "../data/community/creators_and_influencers"

# Cultural sections configuration
CULTURAL_SECTIONS <- list(
  language = list(
    name = "Language & Words",
    icon = "language",
    available = TRUE,
    data_sources = c("tesoro", "dialecto")
  ),
  discover = list(
    name = "Discover Puerto Rico",
    icon = "map-marked-alt",
    available = TRUE,  # Set to TRUE since we now have processed data
    data_sources = c("tripadvisor")
  ),
  community = list(
    name = "Meet the Community",
    icon = "users",
    available = FALSE,
    data_sources = c()
  ),
  food = list(
    name = "Food & Recipes", 
    icon = "utensils",
    available = FALSE,
    data_sources = c()
  ),
  music = list(
    name = "Music & Arts",
    icon = "music", 
    available = FALSE,
    data_sources = c()
  ),
  history = list(
    name = "History & Culture",
    icon = "landmark",
    available = FALSE, 
    data_sources = c()
  )
)

# =============================================================================
# LOAD AND PROCESS DATA
# =============================================================================

cat("=== LOADING TESORO BORICUA CULTURAL PLATFORM DATA ===\n")

# Load language data from both sources
cat("Loading Tesoro data...\n")
tesoro_data <- load_json_data(TESORO_PATH, "Tesoro")

cat("Loading Dialecto data...\n") 
dialecto_data <- load_json_data(DIALECTO_PATH, "Dialecto")

# Combine language datasets
cat("Combining language datasets...\n")
combined_raw <- bind_rows(tesoro_data, dialecto_data)

# Process the combined language data
cat("Processing combined language data...\n")
processed_data <- process_data(combined_raw)

# Load travel data if available
discover_data <- data.frame()
if (CULTURAL_SECTIONS$discover$available) {
  cat("Loading Puerto Rico attractions data...\n")
  discover_file <- file.path(DISCOVER_PATH, "puerto_rico_attractions_processed.json")
  
  tryCatch({
    discover_data <- fromJSON(discover_file, flatten = TRUE)
    discover_data$data_type <- "attraction"
    cat(sprintf("Loaded %d Puerto Rico attractions\n", nrow(discover_data)))
  }, error = function(e) {
    cat(sprintf("Warning: Could not load attractions data: %s\n", e$message))
    discover_data <- data.frame()
  })
} else {
  cat("Attractions data not available (run discover pipeline first)\n")
}

# Create separate datasets for easy filtering
tesoro_only <- filter(processed_data, file_source == "Tesoro")
dialecto_only <- filter(processed_data, file_source == "Dialecto")

# Find overlapping terms (terms that exist in both sources)
tesoro_terms <- unique(str_to_lower(tesoro_only$term_clean))
dialecto_terms <- unique(str_to_lower(dialecto_only$term_clean))
overlapping_terms <- intersect(tesoro_terms, dialecto_terms)

# Mark overlapping entries
processed_data <- processed_data %>%
  mutate(has_overlap = term_lower %in% overlapping_terms)

# Create summary statistics
data_stats <- list(
  total_entries = nrow(processed_data),
  tesoro_entries = nrow(tesoro_only),
  dialecto_entries = nrow(dialecto_only),
  unique_terms = length(unique(processed_data$term_lower)),
  overlapping_terms = length(overlapping_terms),
  letters_covered = length(unique(processed_data$letter))
)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

#' Search function that handles different query types
#' @param data Dataset to search in
#' @param query Search query
#' @param search_type Type of search ("exact", "partial", "contains")
#' @param source_filter Filter by source ("all", "tesoro", "dialecto", "overlap")
search_data <- function(data, query = "", search_type = "partial", source_filter = "all") {
  if (nrow(data) == 0) return(data)
  
  # Apply source filter first
  filtered_data <- switch(source_filter,
    "all" = data,
    "tesoro" = filter(data, file_source == "Tesoro"),
    "dialecto" = filter(data, file_source == "Dialecto"), 
    "overlap" = filter(data, has_overlap == TRUE),
    data
  )
  
  # If no query, return filtered data
  if (is.null(query) || query == "") {
    return(filtered_data)
  }
  
  # Clean query
  query_clean <- str_trim(str_to_lower(query))
  
  # Apply search based on type
  result <- switch(search_type,
    "exact" = filter(filtered_data, term_lower == query_clean),
    "partial" = filter(filtered_data, str_detect(term_lower, fixed(query_clean))),
    "contains" = filter(filtered_data, str_detect(search_text, regex(query_clean, ignore_case = TRUE))),
    filtered_data
  )
  
  return(result)
}

#' Get random entries for learning mode
#' @param data Dataset to sample from
#' @param n Number of entries to return
#' @param source_filter Source filter to apply
get_random_entries <- function(data, n = 5, source_filter = "all") {
  filtered_data <- switch(source_filter,
    "all" = data,
    "tesoro" = filter(data, file_source == "Tesoro"),
    "dialecto" = filter(data, file_source == "Dialecto"),
    "overlap" = filter(data, has_overlap == TRUE),
    data
  )
  
  if (nrow(filtered_data) == 0) return(filtered_data)
  
  n_available <- min(n, nrow(filtered_data))
  sample_indices <- sample(nrow(filtered_data), n_available)
  
  return(filtered_data[sample_indices, ])
}

# =============================================================================
# CULTURAL PLATFORM UTILITY FUNCTIONS (FOR FUTURE EXPANSION)
# =============================================================================

#' Function to load data for any cultural section (extensible)
#' @param section Section name ("language", "food", "music", "history", "discover")
load_section_data <- function(section) {
  if (!section %in% names(CULTURAL_SECTIONS)) {
    warning(paste("Unknown section:", section))
    return(data.frame())
  }
  
  if (!CULTURAL_SECTIONS[[section]]$available) {
    message(paste("Section", section, "is not yet available"))
    return(data.frame())
  }
  
  # Load appropriate data based on section
  if (section == "language") {
    return(processed_data)
  }
  
  if (section == "discover") {
    return(discover_data)
  }
  
  # Future sections would be loaded here
  # if (section == "food") { load_recipe_data() }
  # if (section == "music") { load_music_data() }
  # if (section == "history") { load_history_data() }
  
  return(data.frame())
}

#' Search function for attractions
#' @param data Attraction dataset
#' @param category Category filter
#' @param city City filter
#' @param min_rating Minimum rating filter
search_attractions <- function(data, category = "all", city = "all", min_rating = 0) {
  if (nrow(data) == 0) return(data)
  
  filtered_data <- data
  
  # Apply filters
  if (category != "all") {
    filtered_data <- filter(filtered_data, category == !!category)
  }
  
  if (city != "all") {
    filtered_data <- filter(filtered_data, city == !!city)
  }
  
  if (min_rating > 0) {
    filtered_data <- filter(filtered_data, rating >= min_rating)
  }
  
  # Sort by popularity score
  filtered_data <- arrange(filtered_data, desc(popularity_score))
  
  return(filtered_data)
}

# =============================================================================
# COMPLETION MESSAGE
# =============================================================================

cat("=== CULTURAL PLATFORM LOADING COMPLETE ===\n")
cat(sprintf("🇵🇷 Available sections: Language (%d entries)\n", data_stats$total_entries))
cat(sprintf("🏛️ Tesoro entries: %d\n", data_stats$tesoro_entries))  
cat(sprintf("🗣️ Dialecto entries: %d\n", data_stats$dialecto_entries))
cat(sprintf("🔄 Overlapping terms: %d\n", data_stats$overlapping_terms))
cat(sprintf("🔤 Letters covered: %d\n", data_stats$letters_covered))
cat("📚 Future sections: Discover Puerto Rico, Meet the Community, Food, Music, History (Coming Soon)\n")
cat("🚀 Ready to launch Cultural Learning Platform!\n")