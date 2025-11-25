#!/usr/bin/env python3
"""
Enhanced TripAdvisor Scraper for Puerto Rico Attractions
"""

import os
import json
import time
import random
import logging
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Setup Chrome options
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
driver = webdriver.Chrome(options=options)

# Output folder
OUTPUT_FOLDER = "data/raw/raw_discover"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Base URL
BASE_URL = "https://www.tripadvisor.com"

# Categories to scrape
CATEGORY_URLS = [
    "https://www.tripadvisor.com/Tourism-g147319-Puerto_Rico-Vacations.html",
    "https://www.tripadvisor.com/Attractions-g147319-Activities-Puerto_Rico.html", #Things to Do
    "https://www.tripadvisor.com/Restaurants-g147319-Puerto_Rico.html", # Restaurants
    "https://www.tripadvisor.com/Hotels-g147319-Puerto_Rico-Hotels.html", # Hotels
    "https://www.tripadvisor.com/Attractions-g147320-Activities-c42-Puerto_Rico.html",  # Tours
    "https://www.tripadvisor.com/Attractions-g147320-Activities-c47-Puerto_Rico.html",  # Outdoor
    "https://www.tripadvisor.com/Attractions-g147320-Activities-c49-Puerto_Rico.html",  # Museums
    "https://www.tripadvisor.com/Attractions-g147320-Activities-c61-Puerto_Rico.html",  # Water & Amusement
    "https://www.tripadvisor.com/Attractions-g147320-Activities-c57-Puerto_Rico.html",  # Nature & Parks
]

def random_delay(a=2, b=5):
    time.sleep(random.uniform(a, b))

def scroll_to_bottom(driver, pause=1.0):
    """Scrolls down to the bottom of the page to load dynamic content"""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_attraction_details(url):
    """Extract details from a single attraction page"""
    try:
        driver.get(url)
        random_delay(1, 2)

        scroll_to_bottom(driver)

        wait = WebDriverWait(driver, 10)

        data = {
            "url": url,
            "name": "",
            "description": "",
            "rating": "",
            "review_count": "",
            "location": "",
            "category": "",
            "price_range": "",
            "address": "",
            "phone": "",
            "website": "",
            "hours": "",
            "highlights": [],
            "images": [],
            "top_reviews": []
        }

        # Name
        try:
            name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1[data-test-target='top-info-header']")))
            data["name"] = name.text.strip()
        except: pass

        # Rating and reviews
        try:
            rating_elem = driver.find_element(By.CSS_SELECTOR, "[data-test-target='review-rating'] span")
            data["rating"] = rating_elem.get_attribute("class").split("_")[-1]
            review_elem = driver.find_element(By.CSS_SELECTOR, "[data-test-target='review-count']")
            data["review_count"] = review_elem.text.strip()
        except: pass

        # Description
        try:
            desc_elem = driver.find_element(By.CSS_SELECTOR, "[data-test-target='attraction-detail-about-card'] div[class*='content']")
            data["description"] = desc_elem.text.strip()
        except: pass

        # Category
        try:
            cat_elem = driver.find_element(By.CSS_SELECTOR, "[data-test-target='attraction-detail-category']")
            data["category"] = cat_elem.text.strip()
        except: pass

        # Highlights
        try:
            highlights = driver.find_elements(By.CSS_SELECTOR, "[data-test-target='attraction-highlights'] li")
            data["highlights"] = [h.text.strip() for h in highlights if h.text.strip()]
        except: pass

        # Reviews
        try:
            review_elems = driver.find_elements(By.CSS_SELECTOR, "[data-test-target='review-content']")[:3]
            for r in review_elems:
                txt = r.text.strip()
                if txt:
                    data["top_reviews"].append(txt[:300] + "..." if len(txt) > 300 else txt)
        except: pass

        # Images
        try:
            img_elems = driver.find_elements(By.CSS_SELECTOR, "img[srcset]")
            for img in img_elems[:5]:
                src = img.get_attribute("src")
                if src and src not in data["images"]:
                    data["images"].append(src)
        except: pass

        # Address, phone, website, hours
        try:
            detail_items = driver.find_elements(By.CSS_SELECTOR, ".biGQs._P.fiohW.oWabe")
            for item in detail_items:
                text = item.text
                if "Address" in text:
                    data["address"] = text.split("Address")[1].strip()
                elif "Phone" in text:
                    data["phone"] = text.split("Phone")[1].strip()
                elif "Website" in text:
                    link_elem = item.find_element(By.TAG_NAME, "a")
                    data["website"] = link_elem.get_attribute("href")
                elif "Hours" in text:
                    data["hours"] = text.split("Hours")[1].strip()
        except: pass

        return data

    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {e}")
        return None

def get_attraction_links(category_url):
    """Collect all attraction links from a category page using 'Next' button navigation"""
    links = set()
    page = 1

    while True:
        logger.info(f"Loading page {page}: {category_url}")
        driver.get(category_url)
        scroll_to_bottom(driver, pause=1)
        random_delay()

        try:
            anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/Attraction_Review-']")
            for a in anchors:
                href = a.get_attribute("href")
                if href and '/Attraction_Review-' in href:
                    links.add(href)

            # Check for Next button
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "a.nav.next")
                category_url = urljoin(BASE_URL, next_button.get_attribute("href"))
                page += 1
            except:
                break
        except Exception as e:
            logger.error(f"Error while paginating: {e}")
            break

    return list(links)

def scrape_puerto_rico_attractions():
    all_data = []

    for cat_url in CATEGORY_URLS:
        logger.info(f"Scraping category: {cat_url}")
        attraction_links = get_attraction_links(cat_url)
        logger.info(f"Found {len(attraction_links)} links.")

        for i, link in enumerate(attraction_links, 1):
            logger.info(f"[{i}/{len(attraction_links)}] Scraping: {link}")
            data = extract_attraction_details(link)
            if data and data["name"]:
                all_data.append(data)
            random_delay()

            # Save every 10 entries
            if i % 10 == 0:
                temp_file = os.path.join(OUTPUT_FOLDER, f"puerto_rico_attractions_temp_{i}.json")
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved progress to {temp_file}")

    # Final save
    output_path = os.path.join(OUTPUT_FOLDER, "puerto_rico_attractions_full.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ Finished scraping. Total attractions: {len(all_data)}")
    logger.info(f"💾 Data saved to: {output_path}")
    driver.quit()

if __name__ == "__main__":
    scrape_puerto_rico_attractions()
