from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json
import os
from urllib.parse import urljoin

# --- Setup Headless Chrome ---
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

# Make sure output folder exists
OUTPUT_FOLDER = "data/preprocessed/preprocessed_dialecto"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

#SOURCE_URL = "https://dialectoboricua.com"
BASE_URL = "https://dialectoboricua.com"

def get_letter_links():
    """Extract letter URLs from main page"""
    driver.get(BASE_URL)
    time.sleep(2)
    
    links = driver.find_elements(By.CSS_SELECTOR, "a.letra-enlace")
    letter_links = {}
    
    for link in links:
        letter = link.text.strip().upper()
        href = link.get_attribute("href")
        if letter and href:
            letter_links[letter] = href
            
    return letter_links

def get_word_links(letter_url):
    """Extract all word URLs from a given letter page"""
    driver.get(letter_url)
    time.sleep(2)
    
    word_links = []
    items = driver.find_elements(By.CSS_SELECTOR, "div.elementor-shortcode li a")
    for item in items:
        href = item.get_attribute("href")
        if href and "/la-palabra-del-dia/" in href:
            word_links.append(href)
    
    return word_links

def extract_word_page(word_url):
    """Extract word title and clean paragraph content up to (but not including) the 'Compartir este artículo' section or iframe."""
    driver.get(word_url)
    time.sleep(2)

    try:
        title_elem = driver.find_element(By.CSS_SELECTOR, "h1.elementor-heading-title")
        title = title_elem.text.strip()
    except:
        print(f"⚠️ No title at {word_url}")
        return None, []

    paragraphs = []
    try:
        # Target the main content container
        content_container = driver.find_element(By.CSS_SELECTOR, "div.elementor-widget-theme-post-content div.elementor-widget-container")
        child_elements = content_container.find_elements(By.XPATH, "./*")

        for el in child_elements:
            tag_name = el.tag_name.lower()

            # 🚫 Stop if we reach "Compartir este artículo"
            if tag_name == "h2":
                if el.text.strip().lower() == "compartir este artículo":
                    print(f"🛑 Stopping at 'Compartir este artículo' for {title}")
                    break

            # 🚫 Stop if we hit any iframe
            if tag_name == "iframe":
                print(f"🛑 Stopping at iframe for {title}")
                break

            # ✅ Include <p> paragraphs
            if tag_name == "p":
                text = el.text.strip()
                if text:
                    paragraphs.append(text)

            # ✅ Include blockquotes (they often have examples)
            elif tag_name == "blockquote":
                text = el.text.strip()
                if text:
                    paragraphs.append(text)

    except Exception as e:
        print(f"❌ Error extracting content for {word_url}: {e}")
        return title, []

    if not paragraphs:
        print(f"⚠️ No useful paragraphs found for {title} at {word_url}")

    return title, paragraphs

def crawl_all_letters():
    letter_links = get_letter_links()
    print(f"🔤 Letters found: {list(letter_links.keys())}")

    for letter, letter_url in letter_links.items():
        print(f"\n🔎 Crawling letter: {letter} → {letter_url}")
        word_links = get_word_links(letter_url)
        print(f"  ➤ Found {len(word_links)} word links")

        results = []
        for word_url in word_links:
            title, defs = extract_word_page(word_url)
            if title and defs:
                results.append({
                    "letter": letter,
                    "term": title,
                    "es_definitions": defs,
                    "en_definitions": [],
                    "source": BASE_URL
                })
                print(f"    ✅ {title} ({len(defs)} paragraphs)")
            else:
                print(f"    ❌ Skipped: {word_url}")

        # Save JSON
        filename = os.path.join(OUTPUT_FOLDER, f"dialecto_letter_{letter}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"📁 Saved {len(results)} entries to {filename}")

# --- Run it ---
if __name__ == "__main__":
    try:
        crawl_all_letters()
    finally:
        driver.quit()