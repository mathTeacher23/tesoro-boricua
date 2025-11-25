from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json
import re
from urllib.parse import urljoin, urlparse, parse_qs

# --- Setup Headless Chrome ---
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

BASE_URL = "https://tesoro.pr"
BUSQUEDA_URL = f"{BASE_URL}/busqueda"

# --- Get all available letters ---
def get_letters():
    driver.get(BUSQUEDA_URL)
    time.sleep(2)
    letters = []
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='letra=']")
    for link in links:
        href = link.get_attribute("href")
        parsed = urlparse(href)
        qs = parse_qs(parsed.query)
        letra = qs.get("letra")
        if letra:
            letter = letra[0].strip()
            if letter and letter not in letters:
                letters.append(letter)
    return sorted(letters)


# --- Extract definitions from a word page ---
def extract_clean_definitions(word_url):
    driver.get(word_url)
    time.sleep(1.5)

    try:
        for _ in range(6):
            try:
                word_title = driver.find_element(By.CLASS_NAME, "word-title").text.strip()
                if word_title:
                    break
            except:
                time.sleep(0.5)
        else:
            print(f"⚠️ No word-title found at {word_url}")
            return None, []
    except Exception as e:
        print(f"❌ Exception getting word-title at {word_url}: {e}")
        return None, []

    definitions = []
    try:
        definition_items = driver.find_elements(By.CSS_SELECTOR, "ol.word-definitions.list li.word-definition")
    except:
        definition_items = []

    for item in definition_items:
        spans = item.find_elements(By.CSS_SELECTOR, "div.word-definition-text ol.word-definition-list li span")
        if not spans:
            spans = item.find_elements(By.CSS_SELECTOR, "div.word-definition-text ol.word-definition-list li")

        for span in spans:
            text = span.text.strip()

            if not text:
                try:
                    text = span.get_attribute("innerText").strip()
                except:
                    continue

            if not text:
                continue

            if text.upper() == text and len(text) < 40:
                continue
            if text in {"·", "· ·", "TEMÁTICO ·"}:
                continue

            definitions.append(text)

    if not definitions:
        print(f"⚠️ No definitions for '{word_title}' at {word_url}")

    return word_title, definitions


# --- Get all word URLs for a given letter (multi-page support) ---
def get_all_words_for_letter(letter, sleep_time=2.0, max_pages=1000, max_empty_pages=3):
    page = 1
    all_words = {}
    seen_slugs = set()
    empty_pages = 0

    while True:
        url = f"{BASE_URL}/busqueda?letra={letter}&page={page}"
        driver.get(url)
        time.sleep(sleep_time)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        links = driver.find_elements(By.CSS_SELECTOR, "ol.results-list.list li.results-list-item a")
        if not links:
            print(f"📭 No links on page {page}")
            empty_pages += 1
            if empty_pages >= max_empty_pages:
                print(f"🛑 Reached {empty_pages} empty pages. Stopping.")
                break
            page += 1
            continue

        new_words = 0
        for link in links:
            try:
                word = link.text.strip()
                href = link.get_attribute("href")
                if not href:
                    continue
                full_url = urljoin(BASE_URL, href)
                slug = full_url.split("/lema/")[-1].split("?")[0]
                if slug not in seen_slugs:
                    seen_slugs.add(slug)
                    all_words[word] = full_url
                    new_words += 1
            except Exception as e:
                print(f"⚠️ Error reading link on page {page}: {e}")
                continue

        print(f"📄 Page {page}: {len(links)} links, {new_words} new")
        if new_words == 0:
            empty_pages += 1
            print(f"⚠️ No new words. Empty pages: {empty_pages}")
            if empty_pages >= max_empty_pages:
                print("🛑 Too many empty pages. Stopping.")
                break
        else:
            empty_pages = 0

        page += 1
        if page > max_pages:
            print(f"⛔ Reached max_pages={max_pages}")
            break

    return all_words


# --- Main crawl loop for all letters ---
def crawl_all_letters():
    letters = get_letters()
    #letters = ['b', 'c', 'f', 'l']
    print("🔤 Letters found:", letters)

    for letter in letters:
        print(f"\n🔎 Crawling letter: {letter.upper()}")
        results = {}
        words = get_all_words_for_letter(letter)

        print(f"  ➤ {len(words)} words found for letter '{letter}'")

        for word, url in words.items():
            word_title, defs = extract_clean_definitions(url)
            if word_title and defs:
                results[word_title] = defs
                print(f"    ✅ {word_title}: {len(defs)} defs")
            else:
                print(f"    ❌ Skipped: {word}")

        with open(f"data/raw/raw_tesoro/tesoro_letter_{letter}.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"📁 Saved {len(results)} entries to tesoro_letter_{letter}.json")


# --- Run it ---
if __name__ == "__main__":
    try:
        crawl_all_letters()
    finally:
        driver.quit()
