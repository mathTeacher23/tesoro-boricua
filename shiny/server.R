# =============================================================================
# SERVER.R - Server Logic for Tesoro Boricua Cultural Learning Platform
# =============================================================================

# Define server logic  
server <- function(input, output, session) {
  
  # =============================================================================
  # REACTIVE VALUES
  # =============================================================================
  
  # Store current search results
  search_results <- reactiveVal(processed_data[1:20, ])  # Show first 20 by default
  
  # Store current learning session
  learning_session <- reactiveVal(data.frame())
  
  # =============================================================================
  # NAVIGATION FUNCTIONALITY
  # =============================================================================
  
  # Handle "Start Learning" button on home page
  observeEvent(input$go_language, {
    updateTabItems(session, "sidebar_menu", selected = "lang_search")
  })
  
  # Handle "Explore Attractions" / "Plan Your Trip" button on home page
  observeEvent(input$go_discover, {
    if (CULTURAL_SECTIONS$discover$available) {
      updateTabItems(session, "sidebar_menu", selected = "discover")
    } else {
      # Show modal with coming soon message
      showModal(modalDialog(
      title = "🗺️ Discover Puerto Rico - Coming Soon!",
      div(
        style = "text-align: center; padding: 20px;",
        icon("map-marked-alt", "fa-3x", style = "color: #3498db; margin-bottom: 20px;"),
        h4("We're working on something amazing!", style = "margin-bottom: 15px;"),
        p("Soon you'll be able to:", style = "font-weight: bold; margin-bottom: 10px;"),
        tags$ul(
          style = "text-align: left; display: inline-block; margin-bottom: 20px;",
          tags$li("🏖️ Explore beaches and natural attractions"),
          tags$li("🏛️ Discover historic sites and museums"),
          tags$li("🍴 Find authentic restaurants and local eateries"),
          tags$li("🗺️ Create custom itineraries for your trip"),
          tags$li("📍 Get insider tips from locals"),
          tags$li("🎯 Plan activities based on your interests")
        ),
        p("This section will help you plan the perfect trip to reconnect with your Puerto Rican roots!", 
          style = "font-style: italic; color: #7f8c8d;")
      ),
      footer = modalButton("Got it!"),
      easyClose = TRUE
    ))
    }
  })
  
  # Handle "Meet Creators" button on home page (future implementation)
  observeEvent(input$go_community, {
    # For now, show a modal with coming soon message
    showModal(modalDialog(
      title = "👥 Meet the Community - Coming Soon!",
      div(
        style = "text-align: center; padding: 20px;",
        icon("users", "fa-3x", style = "color: #8e44ad; margin-bottom: 20px;"),
        h4("Connect with Amazing Puerto Rican Creators!", style = "margin-bottom: 15px;"),
        p("This section will feature:", style = "font-weight: bold; margin-bottom: 10px;"),
        tags$ul(
          style = "text-align: left; display: inline-block; margin-bottom: 20px;",
          tags$li("👨‍🍳 Puerto Rican chefs and food content creators on YouTube"),
          tags$li("📚 Educators like Dialecto Boricua teaching language and history"),
          tags$li("🎵 Musicians and artists sharing traditional and modern PR culture"),
          tags$li("✈️ Travel vloggers exploring and showcasing the island"),
          tags$li("📸 Instagram influencers celebrating Puerto Rican identity"),
          tags$li("🎥 TikTok creators making Puerto Rican culture accessible and fun")
        ),
        p("Follow their channels to learn beyond this app and support the community!", 
          style = "font-style: italic; color: #7f8c8d;"),
        br(),
        p("We'll organize creators by category and provide direct links to their social media profiles.", 
          style = "font-size: 12px; color: #95a5a6;")
      ),
      footer = modalButton("Can't wait!"),
      easyClose = TRUE
    ))
  })
  
  # Future navigation handlers for when other sections are implemented
  # observeEvent(input$go_food, { ... })
  # observeEvent(input$go_music, { ... })  
  # observeEvent(input$go_history, { ... })
  
  # =============================================================================
  # LANGUAGE SEARCH FUNCTIONALITY
  # =============================================================================
  
  # Perform search when button is clicked or Enter is pressed
  observeEvent(input$search_btn, {
    perform_search()
  })
  
  # Also search when Enter is pressed in search box
  observeEvent(input$search_query, {
    # Only auto-search if query is not empty and has more than 2 characters
    if (!is.null(input$search_query) && nchar(input$search_query) > 2) {
      perform_search()
    }
  }, ignoreInit = TRUE)
  
  # Perform the actual search
  perform_search <- function() {
    results <- search_data(
      data = processed_data,
      query = input$search_query,
      search_type = input$search_type,
      source_filter = input$source_filter
    )
    
    # Limit results to prevent overwhelming display
    if (nrow(results) > 100) {
      results <- results[1:100, ]
    }
    
    search_results(results)
  }
  
  # Clear search results  
  observeEvent(input$clear_btn, {
    updateTextInput(session, "search_query", value = "")
    search_results(processed_data[1:20, ])
  })
  
  # =============================================================================
  # LEARNING MODE FUNCTIONALITY  
  # =============================================================================
  
  # Generate new learning session
  observeEvent(input$generate_learn, {
    new_session <- get_random_entries(
      data = processed_data,
      n = input$learn_count,
      source_filter = input$learn_source
    )
    learning_session(new_session)
  })
  
  # Initialize learning session on startup
  observe({
    if (nrow(learning_session()) == 0) {
      initial_session <- get_random_entries(processed_data, n = 5, source_filter = "all")
      learning_session(initial_session)
    }
  })
  
  # =============================================================================
  # DISCOVER FUNCTIONALITY
  # =============================================================================
  
  # Store current discover results
  discover_results <- reactiveVal(if(exists("discover_data") && nrow(discover_data) > 0) discover_data[1:20, ] else data.frame())
  
  # Initialize discover filters when data is available
  observe({
    if (CULTURAL_SECTIONS$discover$available && exists("discover_data") && nrow(discover_data) > 0) {
      # Update category choices
      categories <- c("All Categories" = "all", sort(unique(discover_data$category)))
      updateSelectInput(session, "discover_category", choices = categories)
      
      # Update city choices
      cities <- c("All Cities" = "all", sort(unique(discover_data$city[discover_data$city != ""])))
      updateSelectInput(session, "discover_city", choices = cities)
      
      # Set initial results
      discover_results(discover_data[order(-discover_data$popularity_score), ][1:20, ])
    }
  })
  
  # Handle discover filtering
  observeEvent(input$discover_search, {
    if (!CULTURAL_SECTIONS$discover$available || !exists("discover_data")) return()
    
    filtered_data <- discover_data
    
    # Apply category filter
    if (input$discover_category != "all") {
      filtered_data <- filtered_data[filtered_data$category == input$discover_category, ]
    }
    
    # Apply city filter
    if (input$discover_city != "all") {
      filtered_data <- filtered_data[filtered_data$city == input$discover_city, ]
    }
    
    # Apply rating filter
    if (input$discover_rating > 0) {
      filtered_data <- filtered_data[filtered_data$rating >= input$discover_rating, ]
    }
    
    # Sort by popularity
    filtered_data <- filtered_data[order(-filtered_data$popularity_score), ]
    
    # Limit results
    if (nrow(filtered_data) > 100) {
      filtered_data <- filtered_data[1:100, ]
    }
    
    discover_results(filtered_data)
  })

  # =============================================================================
  # OUTPUT RENDERERS - SEARCH TAB
  # =============================================================================
  
  # Search results summary
  output$search_summary <- renderUI({
    results <- search_results()
    n_results <- nrow(results)
    
    if (n_results == 0) {
      div(
        class = "alert alert-warning",
        icon("exclamation-triangle"),
        " No results found. Try a different search term or change the search type."
      )
    } else {
      query_text <- if (is.null(input$search_query) || input$search_query == "") {
        "Showing default entries"
      } else {
        paste("Search:", input$search_query)
      }
      
      source_text <- switch(input$source_filter,
        "all" = "all sources",
        "tesoro" = "Tesoro dictionary", 
        "dialecto" = "Dialecto cultural content",
        "overlap" = "overlapping terms",
        "all sources"
      )
      
      div(
        class = "alert alert-info",
        tags$strong(paste("Found", n_results, "results")), 
        " for '", query_text, "' in ", source_text,
        if (n_results >= 100) " (showing first 100)"
      )
    }
  })
  
  # Main search results display
  output$search_results <- renderUI({
    results <- search_results()
    
    if (nrow(results) == 0) {
      div(
        class = "no-results",
        h3("🔍 No results found"),
        p("Try adjusting your search query or search type.")
      )
    } else {
      # Create cards for each result
      result_cards <- map(1:nrow(results), function(i) {
        row <- results[i, ]
        create_definition_card(row)
      })
      
      do.call(tagList, result_cards)
    }
  })
  
  # Detailed data table 
  output$search_table <- DT::renderDataTable({
    results <- search_results()
    
    if (nrow(results) == 0) return(data.frame())
    
    # Prepare data for table
    table_data <- results %>%
      select(
        Term = term_clean,
        Letter = letter,
        Source = file_source,
        `Spanish Defs` = es_def_count,
        `English Defs` = en_def_count,
        `Has Overlap` = has_overlap,
        `Is Phrase` = is_phrase
      )
    
    DT::datatable(
      table_data,
      options = list(
        pageLength = 25,
        scrollX = TRUE,
        dom = 'frtip'
      ),
      filter = 'top',
      rownames = FALSE
    )
  })
  
  # =============================================================================
  # OUTPUT RENDERERS - LEARNING TAB
  # =============================================================================
  
  # Learning session content
  output$learning_content <- renderUI({
    session_data <- learning_session()
    
    if (nrow(session_data) == 0) {
      div(
        class = "no-results",
        h3("📚 Welcome to Learning Mode!"),
        p("Click 'Generate New Set' to start your learning session."),
        p("This mode presents random words from your selected source to help you practice.")
      )
    } else {
      # Create learning cards
      learning_cards <- map(1:nrow(session_data), function(i) {
        row <- session_data[i, ]
        create_learning_card(row, i)
      })
      
      tagList(
        div(
          class = "alert alert-success",
          tags$strong("📚 Learning Session Active:"), 
          " Practice with ", nrow(session_data), " words/phrases"
        ),
        do.call(tagList, learning_cards)
      )
    }
  })
  
  # =============================================================================
  # OUTPUT RENDERERS - DISCOVER TAB
  # =============================================================================
  
  # Discover results summary
  output$discover_summary <- renderUI({
    results <- discover_results()
    n_results <- nrow(results)
    
    if (n_results == 0) {
      div(
        class = "alert alert-warning",
        icon("exclamation-triangle"),
        " No attractions match your criteria. Try adjusting the filters."
      )
    } else {
      # Create filter summary text
      filter_parts <- c()
      if (input$discover_category != "all") filter_parts <- c(filter_parts, paste("Category:", input$discover_category))
      if (input$discover_city != "all") filter_parts <- c(filter_parts, paste("City:", input$discover_city))
      if (input$discover_rating > 0) filter_parts <- c(filter_parts, paste("Rating ≥", input$discover_rating))
      
      filter_text <- if (length(filter_parts) > 0) {
        paste("Filtered by:", paste(filter_parts, collapse=", "))
      } else {
        "Showing top attractions"
      }
      
      div(
        class = "alert alert-success",
        tags$strong(paste("Found", n_results, "attractions")), 
        " - ", filter_text,
        if (n_results >= 100) " (showing first 100)"
      )
    }
  })
  
  # Main discover results display
  output$discover_results <- renderUI({
    results <- discover_results()
    
    if (nrow(results) == 0) {
      div(
        class = "no-results",
        h3("🗺️ No attractions found"),
        p("Try adjusting your search filters.")
      )
    } else {
      # Create cards for each attraction
      attraction_cards <- map(1:min(nrow(results), 20), function(i) {
        row <- results[i, ]
        create_attraction_card(row)
      })
      
      do.call(tagList, attraction_cards)
    }
  })
  
  # Detailed discover data table
  output$discover_table <- DT::renderDataTable({
    results <- discover_results()
    
    if (nrow(results) == 0) return(data.frame())
    
    # Prepare data for table
    table_data <- results %>%
      select(
        Name = name,
        Category = category,
        City = city,
        Rating = rating,
        Reviews = review_count,
        `Popularity Score` = popularity_score
      ) %>%
      mutate(
        Rating = round(as.numeric(Rating), 1),
        `Popularity Score` = round(as.numeric(`Popularity Score`), 1)
      )
    
    DT::datatable(
      table_data,
      options = list(
        pageLength = 25,
        scrollX = TRUE,
        dom = 'frtip',
        order = list(list(5, 'desc'))  # Sort by popularity score desc
      ),
      filter = 'top',
      rownames = FALSE
    )
  })

  # =============================================================================
  # OUTPUT RENDERERS - STATS TAB
  # =============================================================================
  
  # Value boxes
  output$total_entries_box <- renderValueBox({
    valueBox(
      value = formatC(data_stats$total_entries, format = "d", big.mark = ","),
      subtitle = "Total Entries",
      icon = icon("database"),
      color = "blue"
    )
  })
  
  output$tesoro_entries_box <- renderValueBox({
    valueBox(
      value = formatC(data_stats$tesoro_entries, format = "d", big.mark = ","),
      subtitle = "Tesoro Dictionary",
      icon = icon("book"),
      color = "blue"
    )
  })
  
  output$dialecto_entries_box <- renderValueBox({ 
    valueBox(
      value = formatC(data_stats$dialecto_entries, format = "d", big.mark = ","),
      subtitle = "Dialecto Cultural",
      icon = icon("comments"),
      color = "green"
    )
  })
  
  output$overlap_entries_box <- renderValueBox({
    valueBox(
      value = formatC(data_stats$overlapping_terms, format = "d", big.mark = ","),
      subtitle = "Overlapping Terms",
      icon = icon("intersection"),
      color = "yellow"
    )
  })
  
  # Source distribution plot
  output$source_plot <- renderPlot({
    source_counts <- processed_data %>%
      count(file_source, name = "count")
    
    ggplot(source_counts, aes(x = file_source, y = count, fill = file_source)) +
      geom_col() +
      labs(
        title = "Entries by Source",
        x = "Source",
        y = "Number of Entries"
      ) +
      theme_minimal() +
      scale_fill_manual(values = c("Tesoro" = "#007bff", "Dialecto" = "#28a745")) +
      theme(legend.position = "none")
  })
  
  # Letter distribution plot
  output$letter_plot <- renderPlot({
    letter_counts <- processed_data %>%
      count(letter, name = "count") %>%
      arrange(letter)
    
    ggplot(letter_counts, aes(x = letter, y = count)) +
      geom_col(fill = "#17a2b8") +
      labs(
        title = "Entries by Letter",
        x = "Letter", 
        y = "Number of Entries"
      ) +
      theme_minimal() +
      theme(axis.text.x = element_text(angle = 0))
  })
  
  # Dataset information
  output$dataset_info <- renderUI({
    tagList(
      h4("📊 Dataset Statistics"),
      fluidRow(
        column(6,
          tags$ul(
            tags$li(paste("Total entries:", formatC(data_stats$total_entries, format = "d", big.mark = ","))),
            tags$li(paste("Unique terms:", formatC(data_stats$unique_terms, format = "d", big.mark = ","))), 
            tags$li(paste("Letters covered:", data_stats$letters_covered, "/ 26")),
            tags$li(paste("Overlapping terms:", data_stats$overlapping_terms))
          )
        ),
        column(6,
          tags$ul(
            tags$li(paste("Tesoro entries:", formatC(data_stats$tesoro_entries, format = "d", big.mark = ","))),
            tags$li(paste("Dialecto entries:", formatC(data_stats$dialecto_entries, format = "d", big.mark = ","))),
            tags$li("Sources: tesoro.pr & dialectoboricua.com"),
            tags$li("All content translated ES → EN")
          )
        )
      ),
      hr(),
      h4("ℹ️ About the Data"),
      p("This app combines two Puerto Rican language resources:"),
      tags$ul(
        tags$li(tags$strong("Tesoro"), " - Dictionary-style definitions of Puerto Rican Spanish terms"),
        tags$li(tags$strong("Dialecto"), " - Cultural context and historical information about Puerto Rican expressions")
      ),
      p("All Spanish content has been automatically translated to English to aid learning.")
    )
  })
  
  # Sidebar stats
  output$sidebar_stats <- renderUI({
    results <- search_results()
    learning <- learning_session()
    
    tagList(
      p(paste("📊", formatC(nrow(results), big.mark = ","), "results shown")),
      p(paste("📚", nrow(learning), "words in learning session")),
      p(paste("🎯", data_stats$overlapping_terms, "overlapping terms"))
    )
  })
  
  # =============================================================================
  # HELPER FUNCTIONS FOR UI CREATION
  # =============================================================================
  
  # Create a definition card for search results
  create_definition_card <- function(row) {
    source_class <- if (row$file_source == "Tesoro") "tesoro" else "dialecto"
    badge_class <- if (row$file_source == "Tesoro") "badge-tesoro" else "badge-dialecto"
    
    # Use consolidated text for display
    es_text <- if (!is.na(row$es_text_consolidated) && row$es_text_consolidated != "") {
      row$es_text_consolidated
    } else {
      "No Spanish definitions"
    }
    
    en_text <- if (!is.na(row$en_text_consolidated) && row$en_text_consolidated != "") {
      row$en_text_consolidated  
    } else {
      "No English translations"
    }
    
    div(
      class = paste("definition-card", source_class),
      
      # Header with term and source
      div(
        class = "term-title",
        row$term_clean,
        if (row$has_overlap) span(" 🔄", title = "This term appears in both sources", style = "color: #ffc107;")
      ),
      
      span(class = paste("source-badge", badge_class), row$file_source),
      
      # Spanish definitions
      h5("🇪🇸 Español:", style = "color: #856404; margin-top: 15px;"),
      div(
        class = "spanish-def definition-text", 
        style = "white-space: pre-line;",  # This preserves newlines
        es_text
      ),
      
      # English translations
      h5("🇺🇸 English:", style = "color: #155724; margin-top: 15px;"),
      div(
        class = "english-def definition-text",
        style = "white-space: pre-line;",  # This preserves newlines
        en_text
      )
    )
  }
  
  # Create a learning card with interactive elements
  create_learning_card <- function(row, index) {
    source_class <- if (row$file_source == "Tesoro") "tesoro" else "dialecto"
    
    # Use consolidated text for learning cards too
    es_text <- if (!is.na(row$es_text_consolidated) && row$es_text_consolidated != "") {
      # For learning mode, truncate very long text for better experience
      if (nchar(row$es_text_consolidated) > 800) {
        paste0(substr(row$es_text_consolidated, 1, 800), "\n\n[...continued - see search mode for full text]")
      } else {
        row$es_text_consolidated
      }
    } else {
      "No Spanish definitions"
    }
    
    en_text <- if (!is.na(row$en_text_consolidated) && row$en_text_consolidated != "") {
      # For learning mode, truncate very long text for better experience  
      if (nchar(row$en_text_consolidated) > 800) {
        paste0(substr(row$en_text_consolidated, 1, 800), "\n\n[...continued - see search mode for full text]")
      } else {
        row$en_text_consolidated
      }
    } else {
      "No English translations"
    }
    
    div(
      class = "learning-card",
      
      # Card header
      fluidRow(
        column(8,
          h3(paste(index, ".", row$term_clean), style = "color: #0c5460; margin-bottom: 10px;")
        ),
        column(4,
          div(style = "text-align: right;",
            span(class = "badge badge-info", row$file_source),
            if (row$has_overlap) span(" 🔄", title = "Also in other source")
          )
        )
      ),
      
      # Learning content
      div(
        # Spanish section
        h4("🇪🇸 Spanish:", style = "color: #856404;"),
        div(
          class = "spanish-def",
          style = "white-space: pre-line;",  # Preserves newlines
          es_text
        ),
        
        br(),
        
        # English section 
        h4("🇺🇸 English Translation:", style = "color: #155724;"),
        div(
          class = "english-def",
          style = "white-space: pre-line;",  # Preserves newlines
          en_text
        )
      )
    )
  }
  
  # Create an attraction card for discover results
  create_attraction_card <- function(row) {
    # Handle missing or null values
    rating_display <- if(!is.na(row$rating) && row$rating > 0) {
      paste0("⭐ ", row$rating, "/5.0")
    } else {
      "⭐ No rating"
    }
    
    review_count_display <- if(!is.na(row$review_count) && row$review_count > 0) {
      paste0(" (", formatC(row$review_count, format="d", big.mark=","), " reviews)")
    } else {
      ""
    }
    
    description_text <- if(!is.na(row$description) && row$description != "") {
      # Truncate long descriptions
      if(nchar(row$description) > 300) {
        paste0(substr(row$description, 1, 300), "...")
      } else {
        row$description
      }
    } else {
      "No description available."
    }
    
    highlights <- if(length(row$highlights[[1]]) > 0) {
      row$highlights[[1]][1:min(3, length(row$highlights[[1]]))]  # Show max 3 highlights
    } else {
      c()
    }
    
    div(
      class = "definition-card",
      style = "border-left: 4px solid #3498db;",
      
      # Header with name and category
      div(
        class = "term-title",
        row$name,
        span(
          style = "font-size: 14px; color: #7f8c8d; font-weight: normal; margin-left: 10px;",
          "•", row$category
        )
      ),
      
      # Location and rating
      div(
        style = "margin: 8px 0;",
        if(!is.na(row$city) && row$city != "") {
          span(
            style = "color: #27ae60; margin-right: 15px;",
            icon("map-marker-alt"), " ", row$city
          )
        },
        span(style = "color: #f39c12;", rating_display, review_count_display)
      ),
      
      # Description
      if(description_text != "No description available.") {
        div(
          class = "definition-text",
          style = "margin: 12px 0; line-height: 1.5;",
          description_text
        )
      },
      
      # Highlights
      if(length(highlights) > 0) {
        div(
          style = "margin: 10px 0;",
          h6("Highlights:", style = "color: #2c3e50; margin-bottom: 5px;"),
          tags$ul(
            style = "margin: 0; padding-left: 20px; font-size: 13px;",
            lapply(highlights, function(h) tags$li(h))
          )
        )
      },
      
      # Footer with link
      div(
        style = "margin-top: 15px; text-align: right;",
        if(!is.na(row$url) && row$url != "") {
          tags$a(
            href = row$url,
            target = "_blank",
            class = "btn btn-sm btn-outline-primary",
            icon("external-link-alt"), " View on TripAdvisor"
          )
        }
      )
    )
  }
}