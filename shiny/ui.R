# =============================================================================
# UI.R - User Interface for Tesoro Boricua Cultural Learning Platform
# =============================================================================

# Define the UI
ui <- dashboardPage(
  # =============================================================================
  # HEADER
  # =============================================================================
  dashboardHeader(
    title = "🇵🇷 Tesoro Boricua - Puerto Rican Cultural Learning Platform",
    titleWidth = 450
  ),
  
  # =============================================================================
  # SIDEBAR
  # =============================================================================
  dashboardSidebar(
    width = 300,
    sidebarMenu(
      id = "sidebar_menu",
      
      # Main navigation
      menuItem("🏠 Home", tabName = "home", icon = icon("home")),
      
      # Cultural sections
      menuItem("📖 Language & Words", tabName = "language", icon = icon("language"),
        menuSubItem("🔍 Search & Explore", tabName = "lang_search"),
        menuSubItem("📚 Learning Mode", tabName = "lang_learn"),
        menuSubItem("📊 Language Stats", tabName = "lang_stats")
      ),
      
      # Conditional menu item for Discover Puerto Rico
      if (CULTURAL_SECTIONS$discover$available) {
        menuItem("🗺️ Discover Puerto Rico", tabName = "discover", icon = icon("map-marked-alt"))
      } else {
        menuItem("🗺️ Discover Puerto Rico", tabName = "discover", icon = icon("map-marked-alt"),
          badgeLabel = "Coming Soon", badgeColor = "blue"
        )
      },
      
      menuItem("👥 Meet the Community", tabName = "community", icon = icon("users"),
        badgeLabel = "Coming Soon", badgeColor = "purple"
      ),
      
      menuItem("🍽️ Food & Recipes", tabName = "food", icon = icon("utensils"),
        badgeLabel = "Coming Soon", badgeColor = "orange"
      ),
      
      menuItem("🎵 Music & Arts", tabName = "music", icon = icon("music"),
        badgeLabel = "Coming Soon", badgeColor = "orange"
      ),
      
      menuItem("📚 History & Culture", tabName = "history", icon = icon("landmark"),
        badgeLabel = "Coming Soon", badgeColor = "orange"
      ),
      
      # Conditional sidebar content - shows only for language section
      conditionalPanel(
        condition = "input.sidebar_menu == 'lang_search' || input.sidebar_menu == 'lang_learn'",
        
        # Divider
        br(),
        hr(),
        
        # Search controls
        h4("Language Search Controls", style = "margin-left: 15px; color: #fff;"),
        
        # Search input
        div(style = "margin: 15px;",
          textInput(
            inputId = "search_query",
            label = "Search for words/phrases:",
            placeholder = "e.g., 'fuego', 'culcul', 'chavos'",
            width = "100%"
          )
        ),
        
        # Search type
        div(style = "margin: 15px;",
          selectInput(
            inputId = "search_type",
            label = "Search Type:",
            choices = list(
              "Partial match (recommended)" = "partial",
              "Exact term only" = "exact", 
              "Search in definitions" = "contains"
            ),
            selected = "partial",
            width = "100%"
          )
        ),
        
        # Source filter  
        div(style = "margin: 15px;",
          selectInput(
            inputId = "source_filter",
            label = "Data Source:",
            choices = list(
              "All sources" = "all",
              "Tesoro (Dictionary)" = "tesoro",
              "Dialecto (Cultural)" = "dialecto",
              "Overlapping terms" = "overlap"
            ),
            selected = "all", 
            width = "100%"
          )
        ),
        
        # Action buttons
        div(style = "margin: 15px;",
          actionButton(
            inputId = "search_btn",
            label = "Search",
            icon = icon("search"),
            class = "btn btn-primary",
            width = "48%"
          ),
          actionButton(
            inputId = "clear_btn", 
            label = "Clear",
            icon = icon("eraser"),
            class = "btn btn-secondary",
            width = "48%",
            style = "margin-left: 4%;"
          )
        ),
        
        br(),
        hr(),
        
        # Quick stats
        h4("Language Stats", style = "margin-left: 15px; color: #fff;"),
        div(style = "margin: 15px; color: #fff; font-size: 12px;",
          uiOutput("sidebar_stats")
        )
      )
    )
  ),
  
  # =============================================================================
  # BODY  
  # =============================================================================
  dashboardBody(
    # Custom CSS styling
    tags$head(
      tags$style(HTML("
        .definition-card {
          border: 1px solid #ddd;
          border-radius: 8px;
          padding: 15px;
          margin-bottom: 15px;
          background-color: #f9f9f9;
        }
        .definition-card.tesoro {
          border-left: 4px solid #007bff;
        }
        .definition-card.dialecto {
          border-left: 4px solid #28a745;
        }
        .term-title {
          font-size: 18px;
          font-weight: bold;
          color: #333;
          margin-bottom: 10px;
        }
        .source-badge {
          font-size: 11px;
          padding: 3px 8px;
          border-radius: 12px;
          color: white;
          display: inline-block;
          margin-bottom: 8px;
        }
        .badge-tesoro {
          background-color: #007bff;
        }
        .badge-dialecto {
          background-color: #28a745;
        }
        .definition-text {
          margin: 8px 0;
          line-height: 1.5;
        }
        .spanish-def {
          background-color: #fff3cd;
          padding: 10px;
          border-left: 3px solid #ffc107;
          margin: 5px 0;
          border-radius: 4px;
        }
        .english-def {
          background-color: #d4edda;
          padding: 10px;
          border-left: 3px solid #28a745;
          margin: 5px 0;
          border-radius: 4px;
        }
        .no-results {
          text-align: center;
          padding: 40px;
          color: #666;
          font-style: italic;
        }
        .learning-card {
          border: 2px solid #17a2b8;
          border-radius: 10px;
          padding: 20px;
          margin-bottom: 20px;
          background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        }
      "))
    ),
    
    # Tab items content
    tabItems(
      
      # =============================================================================
      # HOME/LANDING PAGE
      # =============================================================================
      tabItem(
        tabName = "home",
        
        # Welcome header
        fluidRow(
          box(
            title = NULL,
            status = "primary",
            solidHeader = FALSE,
            width = 12,
            div(
              style = "text-align: center; padding: 40px;",
              h1("🇵🇷 ¡Bienvenidos a Tesoro Boricua!", 
                 style = "color: #2c3e50; margin-bottom: 20px;"),
              h2("Welcome to your Puerto Rican Cultural Learning Platform", 
                 style = "color: #7f8c8d; font-weight: 300; margin-bottom: 30px;"),
              p("Reconnect with your roots through language, food, music, and history.", 
                style = "font-size: 18px; color: #5a6c7d; margin-bottom: 40px;")
            )
          )
        ),
        
        # Cultural sections grid - Row 1
        fluidRow(
          # Language section
          column(4,
            box(
              title = NULL,
              status = "success",
              solidHeader = FALSE,
              width = 12,
              height = "300px",
              div(
                style = "text-align: center; padding: 20px;",
                icon("language", "fa-3x", style = "color: #27ae60; margin-bottom: 15px;"),
                h4("📖 Language & Words", style = "color: #2c3e50; margin-bottom: 12px;"),
                p("Explore Puerto Rican Spanish words, phrases, and expressions.", 
                  style = "margin-bottom: 15px; line-height: 1.5; font-size: 13px;"),
                div(
                  tags$span(class = "badge", style = "background-color: #27ae60; margin-right: 8px; font-size: 10px;", 
                           paste(formatC(data_stats$total_entries, format="d", big.mark=","), "entries")),
                  tags$span(class = "badge", style = "background-color: #3498db; font-size: 10px;", "Available Now")
                ),
                br(), br(),
                actionButton("go_language", "Start Learning", 
                           class = "btn btn-success", 
                           style = "width: 80%;")
              )
            )
          ),
          
          # Discover Puerto Rico section  
          column(4,
            box(
              title = NULL,
              status = "info",
              solidHeader = FALSE,
              width = 12,
              height = "300px",
              div(
                style = "text-align: center; padding: 20px;",
                icon("map-marked-alt", "fa-3x", style = "color: #3498db; margin-bottom: 15px;"),
                h4("🗺️ Discover Puerto Rico", style = "color: #2c3e50; margin-bottom: 12px;"),
                p("Plan your journey to the island! Explore tourist sites and create itineraries.", 
                  style = "margin-bottom: 15px; line-height: 1.5; font-size: 13px;"),
                div(
                  tags$span(class = "badge", style = "background-color: #27ae60; margin-right: 8px; font-size: 10px;", "20 attractions"),
                  tags$span(class = "badge", style = "background-color: #3498db; font-size: 10px;", "Available Now")
                ),
                br(), br(),
                actionButton("go_discover", 
                           "Explore Attractions", 
                           class = "btn btn-info", 
                           style = "width: 80%;")
              )
            )
          ),
          
          # Community section
          column(4,
            box(
              title = NULL,
              status = "primary",
              solidHeader = FALSE,
              width = 12,
              height = "300px",
              div(
                style = "text-align: center; padding: 20px; opacity: 0.7;",
                icon("users", "fa-3x", style = "color: #8e44ad; margin-bottom: 15px;"),
                h4("👥 Meet the Community", style = "color: #2c3e50; margin-bottom: 12px;"),
                p("Follow Puerto Rican creators, chefs, historians, and influencers on social media.", 
                  style = "margin-bottom: 15px; line-height: 1.5; font-size: 13px;"),
                div(
                  tags$span(class = "badge", style = "background-color: #8e44ad;", "Coming Soon")
                ),
                br(), br(),
                actionButton("go_community", "Meet Creators", 
                           class = "btn btn-primary", 
                           style = "width: 80%; background-color: #8e44ad; border-color: #8e44ad;", disabled = TRUE)
              )
            )
          )
        ),
        
        # Cultural sections grid - Row 2
        fluidRow(
          # Food section
          column(4,
            box(
              title = NULL,
              status = "warning",
              solidHeader = FALSE,
              width = 12,
              height = "300px",
              div(
                style = "text-align: center; padding: 20px; opacity: 0.7;",
                icon("utensils", "fa-3x", style = "color: #f39c12; margin-bottom: 15px;"),
                h4("🍽️ Food & Recipes", style = "color: #2c3e50; margin-bottom: 12px;"),
                p("Traditional Puerto Rican recipes, cooking techniques, and the stories behind our dishes.", 
                  style = "margin-bottom: 15px; line-height: 1.5; font-size: 13px;"),
                div(
                  tags$span(class = "badge", style = "background-color: #f39c12;", "Coming Soon")
                ),
                br(), br(),
                actionButton("go_food", "Coming Soon", 
                           class = "btn btn-warning", 
                           style = "width: 80%;", disabled = TRUE)
              )
            )
          ),
          
          # Music section
          column(4,
            box(
              title = NULL,
              status = "primary",
              solidHeader = FALSE,
              width = 12,
              height = "300px",
              div(
                style = "text-align: center; padding: 20px; opacity: 0.7;",
                icon("music", "fa-3x", style = "color: #9b59b6; margin-bottom: 15px;"),
                h4("🎵 Music & Arts", style = "color: #2c3e50; margin-bottom: 12px;"),
                p("Learn about bomba, plena, salsa, and other musical traditions that define our culture.", 
                  style = "margin-bottom: 15px; line-height: 1.5; font-size: 13px;"),
                div(
                  tags$span(class = "badge", style = "background-color: #9b59b6;", "Coming Soon")
                ),
                br(), br(),
                actionButton("go_music", "Coming Soon", 
                           class = "btn btn-primary", 
                           style = "width: 80%; background-color: #9b59b6; border-color: #9b59b6;", disabled = TRUE)
              )
            )
          ),
          
          # History section
          column(4,
            box(
              title = NULL,
              status = "danger",
              solidHeader = FALSE,
              width = 12,
              height = "300px",
              div(
                style = "text-align: center; padding: 20px; opacity: 0.7;",
                icon("landmark", "fa-3x", style = "color: #e74c3c; margin-bottom: 15px;"),
                h4("📚 History & Culture", style = "color: #2c3e50; margin-bottom: 12px;"),
                p("Discover Puerto Rican history, from Taíno heritage to modern cultural movements.", 
                  style = "margin-bottom: 15px; line-height: 1.5; font-size: 13px;"),
                div(
                  tags$span(class = "badge", style = "background-color: #e74c3c;", "Coming Soon")
                ),
                br(), br(),
                actionButton("go_history", "Coming Soon", 
                           class = "btn btn-danger", 
                           style = "width: 80%;", disabled = TRUE)
              )
            )
          )
        )
      ),
      
      # =============================================================================
      # LANGUAGE SEARCH & EXPLORE TAB
      # =============================================================================
      tabItem(
        tabName = "lang_search",
        
        # Results summary row
        fluidRow(
          box(
            title = "Language Search Results", 
            status = "primary", 
            solidHeader = TRUE,
            width = 12,
            uiOutput("search_summary")
          )
        ),
        
        # Main results display
        fluidRow(
          box(
            title = "Word Definitions & Translations",
            status = "info",
            solidHeader = TRUE, 
            width = 12,
            height = "600px",
            div(
              style = "height: 500px; overflow-y: auto; padding: 10px;",
              uiOutput("search_results")
            )
          )
        ),
        
        # Data table for advanced users
        fluidRow(
          box(
            title = "Detailed Data Table", 
            status = "warning",
            solidHeader = TRUE,
            collapsible = TRUE,
            collapsed = TRUE,
            width = 12,
            DT::dataTableOutput("search_table")
          )
        )
      ),
      
      # =============================================================================
      # LANGUAGE LEARNING MODE TAB
      # =============================================================================
      tabItem(
        tabName = "lang_learn",
        
        # Learning controls
        fluidRow(
          box(
            title = "Learning Session Controls",
            status = "success", 
            solidHeader = TRUE,
            width = 12,
            
            fluidRow(
              column(4,
                selectInput(
                  "learn_source",
                  "Learn from:",
                  choices = list(
                    "All sources" = "all",
                    "Tesoro (Dictionary focus)" = "tesoro", 
                    "Dialecto (Cultural focus)" = "dialecto",
                    "Overlapping terms" = "overlap"
                  ),
                  selected = "all"
                )
              ),
              column(4,
                numericInput(
                  "learn_count", 
                  "Number of words:",
                  value = 5,
                  min = 1, 
                  max = 20,
                  step = 1
                )
              ),
              column(4,
                br(),
                actionButton(
                  "generate_learn",
                  "Generate New Set",
                  icon = icon("random"),
                  class = "btn btn-success",
                  width = "100%"
                )
              )
            )
          )
        ),
        
        # Learning content  
        fluidRow(
          box(
            title = "📚 Learning Session",
            status = "success",
            solidHeader = TRUE,
            width = 12,
            height = "700px",
            div(
              style = "height: 600px; overflow-y: auto; padding: 15px;",
              uiOutput("learning_content")
            )
          )
        )
      ),
      
      # =============================================================================
      # LANGUAGE DATA OVERVIEW TAB
      # =============================================================================
      tabItem(
        tabName = "lang_stats",
        
        # Summary statistics boxes
        fluidRow(
          valueBoxOutput("total_entries_box", width = 3),
          valueBoxOutput("tesoro_entries_box", width = 3),
          valueBoxOutput("dialecto_entries_box", width = 3), 
          valueBoxOutput("overlap_entries_box", width = 3)
        ),
        
        # Distribution charts and info
        fluidRow(
          box(
            title = "Data Source Breakdown",
            status = "primary",
            solidHeader = TRUE,
            width = 6,
            plotOutput("source_plot", height = "300px")
          ),
          box(
            title = "Letter Distribution", 
            status = "info",
            solidHeader = TRUE,
            width = 6,
            plotOutput("letter_plot", height = "300px")
          )
        ),
        
        # Detailed statistics
        fluidRow(
          box(
            title = "Dataset Information",
            status = "warning",
            solidHeader = TRUE,
            width = 12,
            uiOutput("dataset_info")
          )
        )
      ),
      
      # =============================================================================
      # DISCOVER PUERTO RICO TAB
      # =============================================================================
      tabItem(
        tabName = "discover",
        
        # Conditional content based on data availability
        if (CULTURAL_SECTIONS$discover$available) {
          tagList(
            # Filter controls
            fluidRow(
              box(
                title = "🗺️ Discover Puerto Rico - Filter Attractions",
                status = "info",
                solidHeader = TRUE,
                width = 12,
                fluidRow(
                  column(3,
                    selectInput(
                      "discover_category",
                      "Category:",
                      choices = c("All Categories" = "all"),
                      selected = "all"
                    )
                  ),
                  column(3,
                    selectInput(
                      "discover_city",
                      "City/Region:",
                      choices = c("All Cities" = "all"),
                      selected = "all"
                    )
                  ),
                  column(3,
                    sliderInput(
                      "discover_rating",
                      "Minimum Rating:",
                      min = 0,
                      max = 5,
                      value = 0,
                      step = 0.5
                    )
                  ),
                  column(3,
                    br(),
                    actionButton(
                      "discover_search",
                      "Filter Attractions",
                      class = "btn btn-info",
                      icon = icon("search"),
                      width = "100%"
                    )
                  )
                )
              )
            ),
            
            # Results summary
            fluidRow(
              box(
                title = "Search Results",
                status = "primary",
                solidHeader = TRUE,
                width = 12,
                uiOutput("discover_summary")
              )
            ),
            
            # Attractions display
            fluidRow(
              box(
                title = "Puerto Rico Attractions",
                status = "success",
                solidHeader = TRUE,
                width = 12,
                height = "700px",
                div(
                  style = "height: 600px; overflow-y: auto; padding: 10px;",
                  uiOutput("discover_results")
                )
              )
            ),
            
            # Data table for detailed view
            fluidRow(
              box(
                title = "Detailed Attractions Table",
                status = "warning",
                solidHeader = TRUE,
                collapsible = TRUE,
                collapsed = TRUE,
                width = 12,
                DT::dataTableOutput("discover_table")
              )
            )
          )
        } else {
          # Show coming soon message when data not available
          tagList(
            fluidRow(
              box(
                title = "🗺️ Discover Puerto Rico",
                status = "info",
                solidHeader = TRUE,
                width = 12,
                div(
                  style = "text-align: center; padding: 60px;",
                  icon("map-marked-alt", "fa-4x", style = "color: #3498db; margin-bottom: 30px;"),
                  h2("Travel Data Not Available Yet", style = "color: #2c3e50; margin-bottom: 20px;"),
                  p("To access Puerto Rico attractions and travel planning:", style = "font-size: 16px; margin-bottom: 20px;"),
                  div(
                    style = "text-align: left; display: inline-block; margin-bottom: 30px;",
                    h4("📋 Steps to Enable:"),
                    tags$ol(
                      tags$li("Edit main.py configuration"),
                      tags$li("Set DISCOVER_SCRAPER = True"),
                      tags$li("Set DISCOVER_PROCESS = True"), 
                      tags$li("Set RUN_SHINY_APP = False"),
                      tags$li("Run: python main.py"),
                      tags$li("Wait for scraping to complete"),
                      tags$li("Set RUN_SHINY_APP = True and run again")
                    )
                  ),
                  p("This will scrape TripAdvisor for Puerto Rico attractions and integrate them into the app!",
                    style = "font-style: italic; color: #7f8c8d; font-size: 14px;")
                )
              )
            )
          )
        }
      )
    )
  )
)