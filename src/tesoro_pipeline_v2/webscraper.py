#!/usr/bin/env python3
"""
Improved Web Scraper: Per-Word JSON Output with Detailed Console Logging

Structure:
  letter_p/
    ├── pa.json
    ├── pabellón.json
    └── pabilo.json

Features:
- One JSON file per word
- Organized by letter in folders
- Detailed console logging
- Better error handling
- Progress tracking
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# --- Setup Headless Chrome ---
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

BASE_URL = "https://tesoro.pr"
BUSQUEDA_URL = f"{BASE_URL}/busqueda"


def log_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def log_progress(step, total, message):
    """Print progress with formatting"""
    print(f"  [{step:>4}/{total}] {message}")


def log_success(message):
    """Print success message"""
    print(f"      ✅ {message}")


def log_warning(message):
    """Print warning message"""
    print(f"      ⚠️  {message}")


def log_error(message):
    """Print error message"""
    print(f"      ❌ {message}")


def extract_source_details(def_item):
    """Extract source details from definition item (after clicking [+])"""
    try:
        source_text_elem = def_item.find_element(By.CLASS_NAME, "word-definition-source-text")
        source_text = source_text_elem.text.strip()
        return source_text if source_text else None
    except:
        return None


def extract_word_variants(word_url):
    """Extract all superscript variants with full details"""
    try:
        driver.get(word_url)
        time.sleep(1.5)

        all_variants = []
        word_titles = driver.find_elements(By.CLASS_NAME, "word-title")

        if not word_titles:
            return None

        for variant_idx, title_elem in enumerate(word_titles):
            variant_text = title_elem.text.strip()

            # Extract superscript number
            try:
                sup_elem = title_elem.find_element(By.TAG_NAME, "sup")
                superscript = sup_elem.text.strip()
            except:
                superscript = str(variant_idx + 1)

            # Extract origin from word-header-links (sibling of word-title)
            origin = None
            try:
                # Navigate from word-title to parent word-header, then to word-header-links
                header = title_elem.find_element(By.XPATH, "ancestor::div[@class='word-header']")
                header_links = header.find_element(By.XPATH, "following::div[@class='word-header-links']")
                origin_link = header_links.find_element(By.XPATH, ".//a[contains(@href, 'origenes')]")
                origin = origin_link.text.strip()
            except:
                # Fallback to old method
                try:
                    origin_elem = title_elem.find_element(By.XPATH, "following::p[contains(@class, 'word-origenes')]")
                    origin = origin_elem.text.replace("Origen: ", "").strip()
                except:
                    pass

            # Extract grammar from word-header-links (multiple grammar tags possible)
            grammar = []
            try:
                # Navigate from word-title to parent word-header, then to word-header-links
                header = title_elem.find_element(By.XPATH, "ancestor::div[@class='word-header']")
                header_links = header.find_element(By.XPATH, "following::div[@class='word-header-links']")
                grammar_links = header_links.find_elements(By.XPATH, ".//a[contains(@href, 'marcasGramaticales')]")
                grammar = [g.text.strip() for g in grammar_links]
            except:
                # Fallback to old method
                try:
                    grammar_elem = title_elem.find_element(By.XPATH, "following::p[contains(@class, 'word-grammars')]")
                    grammar_text = grammar_elem.text.replace("Categoría gramatical: ", "").strip()
                    grammar = [g.strip() for g in grammar_text.split(",")]
                except:
                    pass

            # Extract related words (palabras relacionadas)
            related_words = []
            try:
                related_section = title_elem.find_element(By.XPATH, "following::div[contains(@class, 'word-related-words')]")
                related_links = related_section.find_elements(By.TAG_NAME, "a")
                related_words = [link.text.strip() for link in related_links]
            except:
                pass

            # Extract synonyms (sinonimos) from word-table structure
            synonyms = []
            # Extract variants (variantes) from word-table structure
            variants = []
            try:
                # Look for word-table section
                word_table = title_elem.find_element(By.XPATH, "following::div[contains(@class, 'word-table')]")

                # Find all rows in the table
                table_rows = word_table.find_elements(By.CLASS_NAME, "word-table-row")

                for row in table_rows:
                    try:
                        label = row.find_element(By.CLASS_NAME, "word-table-label")
                        label_text = label.text.strip()
                        label_title = label.get_attribute("title") or ""

                        # Get content for this row
                        content = row.find_element(By.CLASS_NAME, "word-table-content")
                        links = content.find_elements(By.CLASS_NAME, "word-table-link")

                        if "Sinónimos" in label_text or "sinonimos" in label_text.lower():
                            # Found synonyms row
                            for link in links:
                                try:
                                    span = link.find_element(By.TAG_NAME, "span")
                                    synonyms.append(span.text.strip())
                                except:
                                    synonyms.append(link.text.strip())

                        elif "Variantes" in label_text or "variantes" in label_text.lower():
                            # Found variants row
                            for link in links:
                                try:
                                    span = link.find_element(By.TAG_NAME, "span")
                                    variants.append(span.text.strip())
                                except:
                                    variants.append(link.text.strip())

                        elif "Relacionadas" in label_text or "relacionadas" in label_text.lower() or "Palabras Relacionadas" in label_title:
                            # Found related words row (check both text and title attribute)
                            for link in links:
                                try:
                                    span = link.find_element(By.TAG_NAME, "span")
                                    related_words.append(span.text.strip())
                                except:
                                    related_words.append(link.text.strip())
                    except:
                        continue
            except:
                pass

            # Extract definitions
            definition_list = []
            try:
                def_container = title_elem.find_element(By.XPATH, "following::ol[contains(@class, 'word-definitions')]")
                def_items = def_container.find_elements(By.CSS_SELECTOR, "li.word-definition")

                for def_idx, def_item in enumerate(def_items):
                    try:
                        # Get definition number
                        def_num = def_item.find_element(By.CLASS_NAME, "word-definition-number").text.strip()
                    except:
                        def_num = str(def_idx + 1)

                    definition_sublist = []

                    # Try to expand source details
                    try:
                        more_button = def_item.find_element(By.CSS_SELECTOR, ".word-definition-source-link-more")
                        driver.execute_script("arguments[0].click();", more_button)
                        time.sleep(0.3)
                    except:
                        pass

                    # Extract sub-definitions (for complex words like piragua)
                    sub_defs = def_item.find_elements(By.CSS_SELECTOR, "li.word-definition-sub")

                    if sub_defs:
                        # Complex word structure with sub-definitions
                        for sub_def in sub_defs:
                            try:
                                sub_item = {
                                    "item": sub_def.find_element(By.CLASS_NAME, "word-definition-sub-letter").text.strip(),
                                    "definition": sub_def.find_element(By.CLASS_NAME, "word-definition-text").text.strip(),
                                    "source": "",
                                    "year": "",
                                    "source_details": None,
                                    "themes": [],
                                    "geography": []
                                }

                                # Extract source/year
                                try:
                                    source_elem = sub_def.find_element(By.CLASS_NAME, "word-definition-source")
                                    source_text = source_elem.text.strip()

                                    # Try to extract year
                                    year_match = None
                                    import re
                                    year_search = re.search(r'\b(1\d{3}|2\d{3})\b', source_text)
                                    if year_search:
                                        year = year_search.group(1)
                                        source = source_text.replace(year, "").strip()
                                        sub_item["year"] = year
                                        sub_item["source"] = source
                                    else:
                                        sub_item["source"] = source_text

                                except:
                                    pass

                                # Extract themes and geography from separate sections
                                try:
                                    # Find all word-definition-themes sections
                                    themes_sections = sub_def.find_elements(By.CLASS_NAME, "word-definition-themes")

                                    for section in themes_sections:
                                        # Check the title to determine if it's a theme or geography section
                                        try:
                                            title_elem = section.find_element(By.CLASS_NAME, "word-definition-themes-title")
                                            title_text = title_elem.text.strip().lower()
                                        except:
                                            title_text = ""

                                        # Get all tags in this section
                                        tags = section.find_elements(By.CLASS_NAME, "word-definition-themes-tag")
                                        tag_list = [tag.text.strip() for tag in tags]

                                        if "temático" in title_text:
                                            # This is a thematic section
                                            sub_item["themes"] = tag_list
                                        elif "geográfico" in title_text:
                                            # This is a geographic section
                                            sub_item["geography"] = tag_list
                                except:
                                    pass

                                # Extract source details (after clicking [+])
                                source_details = extract_source_details(sub_def)
                                if source_details:
                                    sub_item["source_details"] = source_details

                                definition_sublist.append(sub_item)

                            except Exception as e:
                                log_warning(f"Error extracting sub-definition: {str(e)}")
                                continue
                    else:
                        # Simple word structure (e.g., pa, pabilo) - extract definition directly
                        try:
                            # Look for definition in the simple structure: word-definition-text > ol.word-definition-list > li > span
                            def_text_container = def_item.find_element(By.CLASS_NAME, "word-definition-text")
                            def_list_items = def_text_container.find_elements(By.CSS_SELECTOR, "ol.word-definition-list > li")

                            for list_idx, list_item in enumerate(def_list_items):
                                try:
                                    # Get the text from span inside li
                                    definition_text = list_item.find_element(By.TAG_NAME, "span").text.strip()

                                    sub_item = {
                                        "item": chr(97 + list_idx),  # a, b, c, ...
                                        "definition": definition_text,
                                        "source": "",
                                        "year": "",
                                        "source_details": None,
                                        "themes": [],
                                        "geography": []
                                    }

                                    # Try to find all themes and geography in this simple structure
                                    try:
                                        themes_sections = list_item.find_elements(By.CLASS_NAME, "word-definition-themes")

                                        for section in themes_sections:
                                            # Check the title to determine if it's a theme or geography section
                                            try:
                                                title_elem = section.find_element(By.CLASS_NAME, "word-definition-themes-title")
                                                title_text = title_elem.text.strip().lower()
                                            except:
                                                title_text = ""

                                            # Get all tags in this section
                                            tags = section.find_elements(By.CLASS_NAME, "word-definition-themes-tag")
                                            tag_list = [tag.text.strip() for tag in tags]

                                            if "temático" in title_text:
                                                # This is a thematic section
                                                sub_item["themes"] = tag_list
                                            elif "geográfico" in title_text:
                                                # This is a geographic section
                                                sub_item["geography"] = tag_list
                                    except:
                                        pass

                                    definition_sublist.append(sub_item)
                                except Exception as e:
                                    log_warning(f"Error extracting simple definition item: {str(e)}")
                                    continue
                        except Exception as e:
                            log_warning(f"Error extracting simple definition structure: {str(e)}")

                    # For simple or complex words: extract source information from word-definition-source
                    try:
                        source_elem = def_item.find_element(By.CLASS_NAME, "word-definition-source")

                        # Try to get source link text
                        try:
                            source_link = source_elem.find_element(By.CLASS_NAME, "word-definition-source-link")
                            source_text = source_link.text.strip()

                            # Try to extract year from source text
                            import re
                            year_search = re.search(r'\b(1\d{3}|2\d{3})\b', source_text)
                            if year_search:
                                year = year_search.group(1)
                                source = source_text.replace(year, "").strip()
                            else:
                                source = source_text
                                year = ""

                            # Add source/year to all definition_sublist items if they don't have it
                            for sub_item in definition_sublist:
                                if not sub_item.get("source"):
                                    sub_item["source"] = source
                                if not sub_item.get("year"):
                                    sub_item["year"] = year
                        except:
                            pass

                        # Try to extract source details (appears after clicking [+])
                        try:
                            source_details_elem = source_elem.find_element(By.CLASS_NAME, "word-definition-source-text")
                            source_details = source_details_elem.text.strip()

                            # Add source_details to all definition_sublist items if they don't have it
                            for sub_item in definition_sublist:
                                if not sub_item.get("source_details"):
                                    sub_item["source_details"] = source_details
                        except:
                            pass
                    except:
                        pass

                    definition_list.append({
                        "number": def_num,
                        "definition_sublist": definition_sublist
                    })

            except Exception as e:
                log_warning(f"Error extracting definitions: {str(e)}")

            variant_entry = {
                "superscript": superscript,
                "details": {
                    "origin": origin,
                    "grammar": grammar,
                    "relatedWords": related_words,
                    "synonyms": synonyms,
                    "variants": variants,
                    "definition_list": definition_list
                }
            }

            all_variants.append(variant_entry)

        return all_variants if all_variants else None

    except Exception as e:
        log_error(f"extract_word_variants failed: {str(e)}")
        return None


def get_first_n_words_for_letter(letter, n=None, sleep_time=2.0, max_pages=1000, max_empty_pages=3):
    """Get first N words for a letter - scraping from all search pages"""
    try:
        if n is None:
            log_section(f"Fetching ALL words starting with '{letter.upper()}'")
        else:
            log_section(f"Fetching first {n} words starting with '{letter.upper()}'")

        words = {}
        seen_slugs = set()
        page = 1
        empty_pages = 0

        while page <= max_pages:
            if n is not None and len(words) >= n:
                break

            # Go to the search page for the letter with pagination
            search_url = f"{BASE_URL}/busqueda?letra={letter.lower()}&page={page}"
            driver.get(search_url)
            time.sleep(sleep_time)

            # Scroll to bottom to ensure all links are loaded
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            # Use CSS selector like the old script (more reliable)
            word_links = driver.find_elements(By.CSS_SELECTOR, "ol.results-list.list li.results-list-item a")

            if not word_links:
                log_warning(f"No word links found on page {page}")
                empty_pages += 1
                if empty_pages >= max_empty_pages:
                    log_success(f"Reached {empty_pages} empty pages. Stopping.")
                    break
                page += 1
                continue

            page_found = 0
            for link in word_links:
                if n is not None and len(words) >= n:
                    break

                try:
                    text = link.text.strip()
                    href = link.get_attribute("href")

                    if not href:
                        continue

                    # Use slug-based deduplication (more reliable than text)
                    slug = href.split("/lema/")[-1].split("?")[0]

                    if slug not in seen_slugs:
                        seen_slugs.add(slug)
                        words[text] = href
                        page_found += 1
                        total_display = n if n is not None else "?"
                        log_progress(len(words), total_display, f"Found: {text}")
                except Exception as e:
                    log_warning(f"Error reading link: {str(e)}")
                    continue

            log_progress(page, max_pages, f"Page {page}: {len(word_links)} links, {page_found} new")

            if page_found == 0:
                # No new words found on this page
                empty_pages += 1
                log_warning(f"No new words. Empty pages: {empty_pages}")
                if empty_pages >= max_empty_pages:
                    log_success(f"Too many empty pages. Stopping.")
                    break
            else:
                # Reset counter when we find new words
                empty_pages = 0

            page += 1

        log_success(f"Retrieved {len(words)} words")
        return words

    except Exception as e:
        log_error(f"Failed to get words: {str(e)}")
        return {}


def scrape_letter_words(letter, word_count=4, output_base_dir=None):
    """Scrape words for a letter, save each word as separate JSON in raw folder"""

    # Use parent data directory by default
    if output_base_dir is None:
        output_base_dir = str(Path(__file__).parent.parent / "data")

    log_section(f"SCRAPING LETTER '{letter.upper()}' - First {word_count} words")

    # Get words
    words = get_first_n_words_for_letter(letter, word_count)

    if not words:
        log_error(f"No words found for letter {letter}")
        return False

    # Create raw data folder
    raw_folder = os.path.join(output_base_dir, f"raw/raw_tesoro_v2/{letter.lower()}")
    os.makedirs(raw_folder, exist_ok=True)
    log_success(f"Created folder: {raw_folder}")

    # Process each word
    processed = 0
    failed = 0

    for idx, (word, url) in enumerate(words.items(), 1):
        log_progress(idx, len(words), f"Processing: {word}")

        try:
            # Extract variants
            variants = extract_word_variants(url)

            if variants:
                # Create word JSON
                word_json = {word: variants}

                # Save to individual file in raw folder
                output_file = os.path.join(raw_folder, f"{word.lower().replace(' ', '_')}.json")
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(word_json, f, indent=2, ensure_ascii=False)

                log_success(f"Saved {len(variants)} variant(s) to {os.path.basename(output_file)}")
                processed += 1

            else:
                log_warning(f"No variants found for {word}")
                failed += 1

        except Exception as e:
            log_error(f"Failed to process {word}: {str(e)}")
            failed += 1

    # Summary
    log_section(f"SCRAPING COMPLETE")
    print(f"  Letter:        {letter.upper()}")
    print(f"  Processed:     {processed}")
    print(f"  Failed:        {failed}")
    print(f"  Raw folder:    {raw_folder}")
    print(f"  Timestamp:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    return processed > 0


def consolidate_letter_data(letter, data_dir="./data"):
    """Run consolidation script for a letter"""
    try:
        log_section(f"CONSOLIDATING LETTER '{letter.upper()}'")

        # Import and run consolidation
        from consolidate_letter import consolidate_letter

        success = consolidate_letter(
            letter,
            input_dir=data_dir,
            verbose=True,
            raw_folder="raw_tesoro_v2",
            preprocessed_folder="preprocessed_tesoro_v2"
        )

        if success:
            log_success(f"Consolidation completed for letter {letter.upper()}")
            return True
        else:
            log_warning(f"Consolidation had issues for letter {letter.upper()}")
            return False

    except ImportError:
        log_error("consolidate_letter module not found in current directory")
        return False
    except Exception as e:
        log_error(f"Consolidation failed: {str(e)}")
        return False


def main():
    """Main entry point"""
    try:
        print("\n" + "🔍 " * 20)
        print("TESORO.PR WEB SCRAPER - Per-Word JSON Output with Consolidation")
        print("🔍 " * 20 + "\n")

        # Get letters from command line argument or use all letters
        letters_to_scrape = []
        word_count = None

        if len(sys.argv) > 1:
            if sys.argv[1].lower() == "all":
                # Scrape all letters
                letters_to_scrape = [chr(i) for i in range(ord('a'), ord('z') + 1)] + ['ñ']
            else:
                # Single letter
                letters_to_scrape = [sys.argv[1]]
        else:
            # Default to all letters
            letters_to_scrape = [chr(i) for i in range(ord('a'), ord('z') + 1)] + ['ñ']

        if len(sys.argv) > 2:
            try:
                word_count = int(sys.argv[2])
            except ValueError:
                print(f"Warning: Could not parse word_count '{sys.argv[2]}', using all words")

        # Scrape each letter
        total_letters = len(letters_to_scrape)
        successful_letters = 0
        failed_letters = 0

        for idx, letter in enumerate(letters_to_scrape, 1):
            print(f"\n{'='*80}")
            print(f"  LETTER {idx}/{total_letters}: {letter.upper()}")
            print(f"{'='*80}\n")

            # Scrape the letter (uses parent data directory by default)
            scrape_success = scrape_letter_words(letter=letter, word_count=word_count)

            if scrape_success:
                # Run consolidation after scraping completes
                consolidate_letter_data(letter, data_dir=str(Path(__file__).parent.parent / "data"))
                successful_letters += 1
            else:
                failed_letters += 1
                print(f"⚠️  Skipping consolidation for letter {letter.upper()} due to scraping issues.")

        # Final summary
        print(f"\n{'='*80}")
        print(f"  OVERALL SUMMARY")
        print(f"{'='*80}\n")
        print(f"  Total letters:       {total_letters}")
        print(f"  Successful:          {successful_letters}")
        print(f"  Failed:              {failed_letters}")
        print(f"  Timestamp:           {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        if successful_letters == total_letters:
            print("✅ All letters scraped and consolidated successfully!")
        else:
            print(f"⚠️  Completed with {failed_letters} letter(s) failed.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
    finally:
        driver.quit()
        print("\n✅ Browser closed\n")


if __name__ == "__main__":
    main()
