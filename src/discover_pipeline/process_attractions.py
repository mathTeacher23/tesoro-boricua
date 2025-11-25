#!/usr/bin/env python3
"""
Process and clean TripAdvisor attraction data
Structures data for Shiny app consumption
"""

import json
import re
import selenium
from pathlib import Path
from datetime import datetime

# Input/Output paths
INPUT_DIR = Path("data/raw/raw_discover")
OUTPUT_DIR = Path("data/preprocessed/preprocessed_discover")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def clean_rating(rating_str):
    """Extract numerical rating from TripAdvisor rating class"""
    if not rating_str:
        return 0.0
    
    # TripAdvisor uses class names like "ui_bubble_rating bubble_50" for 5.0 rating
    try:
        if "bubble_" in rating_str:
            rating_part = rating_str.split("bubble_")[-1].split()[0]
            return float(rating_part) / 10.0  # Convert 50 to 5.0
        return 0.0
    except (ValueError, IndexError):
        return 0.0

def clean_review_count(review_count_str):
    """Extract numerical review count"""
    if not review_count_str:
        return 0
    
    try:
        # Extract numbers from strings like "1,234 reviews"
        numbers = re.findall(r'[\d,]+', review_count_str)
        if numbers:
            return int(numbers[0].replace(',', ''))
        return 0
    except ValueError:
        return 0

def categorize_attraction(category, name, description, highlights):
    """Categorize attractions into standardized categories"""
    category = category.lower() if category else ""
    name = name.lower() if name else ""
    description = description.lower() if description else ""
    highlights_text = " ".join(highlights).lower() if highlights else ""
    
    all_text = f"{category} {name} {description} {highlights_text}"
    
    # Define category mappings
    if any(word in all_text for word in ["beach", "playa", "coast", "swim", "snorkel", "surf"]):
        return "Beaches & Water Activities"
    elif any(word in all_text for word in ["museum", "historic", "history", "fort", "castle", "monument"]):
        return "Historic Sites & Museums"
    elif any(word in all_text for word in ["nature", "forest", "park", "hike", "trail", "rainforest", "mountain"]):
        return "Nature & Parks"
    elif any(word in all_text for word in ["food", "restaurant", "cuisine", "dining", "eat", "drink", "bar"]):
        return "Food & Dining"
    elif any(word in all_text for word in ["tour", "excursion", "experience", "adventure", "activity"]):
        return "Tours & Experiences"
    elif any(word in all_text for word in ["art", "gallery", "culture", "music", "show", "theater", "festival"]):
        return "Arts & Culture"
    elif any(word in all_text for word in ["shop", "market", "shopping", "boutique", "store"]):
        return "Shopping"
    elif any(word in all_text for word in ["hotel", "resort", "accommodation", "stay", "spa"]):
        return "Hotels & Resorts"
    elif any(word in all_text for word in ["nightlife", "bar", "club", "entertainment", "music", "dance", "party"]):
        return "Nightlife & Entertainment"
    else:
        return "Other Attractions"

def extract_location_details(location_str):
    """Extract city/region from location string"""
    if not location_str:
        return {"city": "", "region": "Puerto Rico"}
    
    # Common Puerto Rico cities and regions
    pr_cities = [
        "san juan", "bayamon", "carolina", "ponce", "caguas", "guaynabo", "mayaguez",
        "trujillo alto", "arecibo", "fajardo", "vega baja", "dorado", "rincon",
        "culebra", "vieques", "aguadilla", "camuy", "isabela", "luquillo", "ceiba"
    ]
    
    location_lower = location_str.lower()
    
    for city in pr_cities:
        if city in location_lower:
            return {"city": city.title(), "region": "Puerto Rico"}
    
    return {"city": location_str, "region": "Puerto Rico"}

def calculate_popularity_score(rating, review_count, category):
    """Calculate a popularity score for ranking"""
    try:
        rating = float(rating) if rating else 0
        review_count = int(review_count) if review_count else 0
        
        # Base score from rating and reviews
        score = (rating * 20) + (min(review_count, 5000) / 50)
        
        # Boost certain categories
        category_boosts = {
            "Historic Sites & Museums": 1.2,
            "Nature & Parks": 1.1,
            "Beaches & Water Activities": 1.3,
            "Arts & Culture": 1.1,
            "Food & Dining": 1.2,
            "Tours & Experiences": 1.15,
            "Hotels & Resorts": 1.0,
            "Shopping": 0.9,
            "Nightlife & Entertainment": 1.05
        }
        
        return score * category_boosts.get(category, 1.0)
    except (ValueError, TypeError):
        return 0

def process_attractions_data():
    """Main function to process attraction data"""
    print("🏝️ PROCESSING PUERTO RICO COMPREHENSIVE DATA")
    print("=" * 50)
    
    # Try comprehensive data first, fallback to attractions only
    input_file = INPUT_DIR / "comprehensive_puerto_rico_data.json"
    if not input_file.exists():
        input_file = INPUT_DIR / "puerto_rico_attractions.json"
    
    if not input_file.exists():
        print("❌ Input file not found:", input_file)
        print("   Run the scraper first: python src/discover_pipeline/tripadvisor_scraper.py")
        return
    
    with open(input_file, "r", encoding="utf-8") as f:
        raw_attractions = json.load(f)
    
    print(f"📊 Processing {len(raw_attractions)} raw attractions...")
    
    processed_attractions = []
    
    for i, attraction in enumerate(raw_attractions, 1):
        try:
            # Clean and structure the data
            processed = {
                # Basic info
                "id": f"pr_attraction_{i}",
                "name": attraction.get("name", "").strip(),
                "description": attraction.get("description", "").strip(),
                "url": attraction.get("url", ""),
                
                # Location info
                "location_raw": attraction.get("location", ""),
                **extract_location_details(attraction.get("location", "")),
                
                # Rating and popularity
                "rating": clean_rating(attraction.get("rating", "")),
                "review_count": clean_review_count(attraction.get("review_count", "")),
                
                # Category
                "category_raw": attraction.get("category", ""),
                "category": categorize_attraction(
                    attraction.get("category", ""),
                    attraction.get("name", ""),
                    attraction.get("description", ""),
                    attraction.get("highlights", [])
                ),
                
                # Additional details
                "highlights": attraction.get("highlights", []),
                "top_reviews": attraction.get("top_reviews", []),
                "address": attraction.get("address", ""),
                "phone": attraction.get("phone", ""),
                "website": attraction.get("website", ""),
                "price_range": attraction.get("price_range", ""),
                "hours": attraction.get("hours", ""),
                
                # Metadata
                "scraped_date": datetime.now().isoformat(),
                "data_source": "TripAdvisor"
            }
            
            # Calculate popularity score
            processed["popularity_score"] = calculate_popularity_score(
                processed["rating"],
                processed["review_count"], 
                processed["category"]
            )
            
            # Only include if we have basic info
            if processed["name"] and len(processed["name"]) > 2:
                processed_attractions.append(processed)
                
                if i % 50 == 0:
                    print(f"  ✅ Processed {i}/{len(raw_attractions)} attractions")
                    
        except Exception as e:
            print(f"  ⚠️ Error processing attraction {i}: {e}")
            continue
    
    # Sort by popularity score
    processed_attractions.sort(key=lambda x: x["popularity_score"], reverse=True)
    
    # Save processed data
    output_file = OUTPUT_DIR / "puerto_rico_attractions_processed.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(processed_attractions, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ PROCESSING COMPLETE!")
    print(f"📁 Saved {len(processed_attractions)} processed attractions to {output_file}")
    
    # Print summary statistics
    print(f"\n📊 SUMMARY STATISTICS:")
    print(f"   Total attractions: {len(processed_attractions)}")
    print(f"   Average rating: {sum(a['rating'] for a in processed_attractions if a['rating']) / len([a for a in processed_attractions if a['rating']]):.1f}")
    
    # Category breakdown
    categories = {}
    for attraction in processed_attractions:
        cat = attraction["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n🗂️ CATEGORIES:")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"   {category}: {count}")
    
    # Top attractions
    print(f"\n🏆 TOP 10 ATTRACTIONS:")
    for i, attraction in enumerate(processed_attractions[:10], 1):
        rating_str = f"({attraction['rating']}/5.0)" if attraction['rating'] else "(No rating)"
        print(f"   {i:2d}. {attraction['name']} {rating_str} - {attraction['category']}")

if __name__ == "__main__":
    process_attractions_data()