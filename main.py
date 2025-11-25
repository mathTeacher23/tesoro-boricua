#!/usr/bin/env python3
"""
Main pipeline runner for Tesoro Boricua project.
Configure which parts of each pipeline to run using the flags below.
"""

import subprocess
import multiprocessing
import sys
from pathlib import Path

# =============================================================================
# CONFIGURATION - Set to True/False to enable/disable each step
# =============================================================================

# Tesoro Pipeline Controls
TESORO_WEBSCRAPER = False    # Scrape tesoro.pr for raw data
TESORO_PREPROCESS = False    # Transform raw data format
TESORO_TRANSLATE = False     # Translate Spanish to English

# Dialecto Pipeline Controls  
DIALECTO_WEBSCRAPER = False  # Scrape dialectoboricua.com for data
DIALECTO_TRANSLATE = False   # Translate Spanish to English

# Discover Pipeline Controls
DISCOVER_SCRAPER = True     # Scrape TripAdvisor for Puerto Rico attractions
DISCOVER_PROCESS = True     # Process and clean attraction data

# Application Controls
RUN_SHINY_APP = True       # Launch the Shiny learning app
SHINY_PORT = 3838          # Port for Shiny app (default 3838)
SHINY_HOST = "127.0.0.1"   # Host for Shiny app (localhost)

# Execution Controls
RUN_ASYNC = True            # Run pipelines in parallel (True) or sequential (False)
VERBOSE = True              # Print detailed output

# =============================================================================
# PIPELINE FUNCTIONS
# =============================================================================

def run_command(command, description):
    """Run a subprocess command with error handling."""
    if VERBOSE:
        print(f"🚀 Starting: {description}")
        print(f"   Command: {' '.join(command)}")
    
    try:
        subprocess.run(
            command, 
            cwd=Path.cwd(),
            capture_output=not VERBOSE,
            text=True,
            check=True
        )
        if VERBOSE:
            print(f"✅ Completed: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {description}")
        print(f"   Error: {e}")
        if not VERBOSE and e.stdout:
            print(f"   Output: {e.stdout}")
        if not VERBOSE and e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def run_tesoro_pipeline():
    """Execute the Tesoro pipeline steps based on configuration."""
    if not any([TESORO_WEBSCRAPER, TESORO_PREPROCESS, TESORO_TRANSLATE]):
        if VERBOSE:
            print("⏭️  Skipping Tesoro pipeline (all steps disabled)")
        return True
    
    print("\n🏛️  TESORO PIPELINE")
    print("=" * 50)
    
    success = True
    
    if TESORO_WEBSCRAPER:
        success &= run_command(
            ["python", "src/tesoro_pipeline/webscraper.py"],
            "Tesoro webscraper"
        )
    
    if TESORO_PREPROCESS and success:
        success &= run_command(
            ["python", "src/tesoro_pipeline/preprocess.py"],
            "Tesoro preprocessor"
        )
    
    if TESORO_TRANSLATE and success:
        success &= run_command(
            ["python", "src/tesoro_pipeline/translate.py"],
            "Tesoro translator"
        )
    
    if success:
        print("✅ Tesoro pipeline completed successfully")
    else:
        print("❌ Tesoro pipeline failed")
    
    return success

def run_dialecto_pipeline():
    """Execute the Dialecto pipeline steps based on configuration."""
    if not any([DIALECTO_WEBSCRAPER, DIALECTO_TRANSLATE]):
        if VERBOSE:
            print("⏭️  Skipping Dialecto pipeline (all steps disabled)")
        return True
    
    print("\n🗣️  DIALECTO PIPELINE")
    print("=" * 50)
    
    success = True
    
    if DIALECTO_WEBSCRAPER:
        success &= run_command(
            ["python", "src/dialecto_pipeline/webscraper.py"],
            "Dialecto webscraper"
        )
    
    if DIALECTO_TRANSLATE and success:
        success &= run_command(
            ["python", "src/dialecto_pipeline/translate.py"],
            "Dialecto translator"
        )
    
    if success:
        print("✅ Dialecto pipeline completed successfully")
    else:
        print("❌ Dialecto pipeline failed")
    
    return success

def run_pipelines_async():
    """Run all pipelines in parallel using multiprocessing."""
    print("🔄 Running pipelines in parallel...")
    
    with multiprocessing.Pool(processes=3) as pool:
        # Submit all pipelines
        tesoro_result = pool.apply_async(run_tesoro_pipeline)
        dialecto_result = pool.apply_async(run_dialecto_pipeline)
        discover_result = pool.apply_async(run_discover_pipeline)
        
        # Wait for results
        tesoro_success = tesoro_result.get()
        dialecto_success = dialecto_result.get()
        discover_success = discover_result.get()
    
    return tesoro_success and dialecto_success and discover_success

def run_pipelines_sequential():
    """Run pipelines one after another."""
    print("📋 Running pipelines sequentially...")
    
    tesoro_success = run_tesoro_pipeline()
    dialecto_success = run_dialecto_pipeline()
    discover_success = run_discover_pipeline()
    
    return tesoro_success and dialecto_success and discover_success

def run_discover_pipeline():
    """Execute the Discover pipeline steps based on configuration."""
    if not any([DISCOVER_SCRAPER, DISCOVER_PROCESS]):
        if VERBOSE:
            print("⏭️  Skipping Discover pipeline (all steps disabled)")
        return True
    
    print("\n🗺️  DISCOVER PIPELINE")
    print("=" * 50)
    
    success = True
    
    if DISCOVER_SCRAPER:
        success &= run_command(
            ["python", "src/discover_pipeline/tripadvisor_scraper.py"],
            "TripAdvisor attractions scraper"
        )
    
    if DISCOVER_PROCESS and success:
        success &= run_command(
            ["python", "src/discover_pipeline/process_attractions.py"],
            "Attractions data processor"
        )
    
    if success:
        print("✅ Discover pipeline completed successfully")
    else:
        print("❌ Discover pipeline failed")
    
    return success

def run_shiny_app():
    """Launch the Shiny learning app."""
    print("\n🇵🇷 SHINY LEARNING APP")
    print("=" * 50)
    
    # Check if shiny directory exists
    shiny_dir = Path("shiny")
    if not shiny_dir.exists():
        print("❌ Shiny directory not found!")
        print("   Expected: ./shiny/")
        return False
    
    # Check for required Shiny files
    required_files = ["global.R", "ui.R", "server.R"]
    missing_files = [f for f in required_files if not (shiny_dir / f).exists()]
    
    if missing_files:
        print(f"❌ Missing Shiny files: {', '.join(missing_files)}")
        return False
    
    print("🚀 Launching Shiny app...")
    print(f"   📍 Host: {SHINY_HOST}")
    print(f"   🔌 Port: {SHINY_PORT}")
    print(f"   🌐 URL: http://{SHINY_HOST}:{SHINY_PORT}")
    print("\n💡 The app will open in your browser automatically")
    print("   Press Ctrl+C to stop the app\n")
    
    # Create R command to run Shiny app
    r_command = [
        "Rscript", "-e",
        f"library(shiny); runApp('.', host='{SHINY_HOST}', port={SHINY_PORT}, launch.browser=TRUE)"
    ]
    
    try:
        # Change to shiny directory and run
        result = subprocess.run(
            r_command,
            cwd=shiny_dir,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Shiny app closed successfully")
            return True
        else:
            print("⚠️ Shiny app closed with warnings")
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch Shiny app: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Install R: https://www.r-project.org/")
        print("   2. Install required packages:")
        print("      Rscript -e \"install.packages(c('shiny','shinydashboard','DT','jsonlite','dplyr','stringr','purrr','ggplot2'))\"")
        return False
    except FileNotFoundError:
        print("❌ R/Rscript not found!")
        print("\n🔧 Install R first:")
        print("   macOS: brew install r")
        print("   Ubuntu: sudo apt-get install r-base")
        print("   Windows: Download from https://www.r-project.org/")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Shiny app stopped by user")
        return True

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main entry point."""
    print("🇵🇷 TESORO BORICUA PIPELINE RUNNER")
    print("=" * 60)
    
    # Check if anything is enabled
    pipeline_steps = [
        TESORO_WEBSCRAPER, TESORO_PREPROCESS, TESORO_TRANSLATE,
        DIALECTO_WEBSCRAPER, DIALECTO_TRANSLATE,
        DISCOVER_SCRAPER, DISCOVER_PROCESS
    ]
    
    # Special handling for Shiny app
    if RUN_SHINY_APP:
        print("🎯 Shiny app mode selected")
        return 0 if run_shiny_app() else 1
    
    if not any(pipeline_steps):
        print("⚠️  No pipeline steps are enabled!")
        print("   💡 To run the Shiny learning app, set RUN_SHINY_APP = True")
        print("   💡 To run data pipelines, enable the desired pipeline steps")
        print("   Edit the configuration flags at the top of main.py")
        return 1
    
    # Show configuration
    if VERBOSE:
        print("\n📋 Pipeline Configuration:")
        print(f"   Tesoro Webscraper:    {'✅' if TESORO_WEBSCRAPER else '❌'}")
        print(f"   Tesoro Preprocess:    {'✅' if TESORO_PREPROCESS else '❌'}")
        print(f"   Tesoro Translate:     {'✅' if TESORO_TRANSLATE else '❌'}")
        print(f"   Dialecto Webscraper:  {'✅' if DIALECTO_WEBSCRAPER else '❌'}")
        print(f"   Dialecto Translate:   {'✅' if DIALECTO_TRANSLATE else '❌'}")
        print(f"   Discover Scraper:     {'✅' if DISCOVER_SCRAPER else '❌'}")
        print(f"   Discover Process:     {'✅' if DISCOVER_PROCESS else '❌'}")
        print(f"   Run Async:            {'✅' if RUN_ASYNC else '❌'}")
        print()
    
    # Execute pipelines
    try:
        if RUN_ASYNC:
            success = run_pipelines_async()
        else:
            success = run_pipelines_sequential()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 All enabled pipelines completed successfully!")
            return 0
        else:
            print("💥 Some pipelines failed. Check the output above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n🛑 Pipeline execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())