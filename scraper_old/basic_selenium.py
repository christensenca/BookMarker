import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

NOTEBOOK_URL = "https://read.amazon.com/notebook"

# Set up the Chrome driver (using webdriver-manager for simplicity)
try:
    from webdriver_manager.chrome import ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
except:
    print("webdriver_manager not found or an error occurred. Ensure you have the correct driver installed and in your PATH.")
    # Fallback for manual driver path
    # driver = webdriver.Chrome(executable_path='/path/to/chromedriver')


def scrape_highlights(driver):
    """
    Navigates to each book and extracts highlights with metadata into a JSON structure.
    """
    
    highlights_data = {}
    
    # Wait for the main library content to load
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "library"))
        )
        print("Library page loaded. Starting scraping sequence.")
    except:
        print("Could not load library page within 30 seconds. Exiting.")
        return highlights_data

    # Find all book titles and extract book info (author, last accessed date, image URL)
    book_elements = driver.find_elements(By.CSS_SELECTOR, "div.kp-notebook-library-each-book")
    book_info = {}  # Store author, last accessed date, and image URL
    
    for book_el in book_elements:
        try:
            title_el = book_el.find_element(By.CSS_SELECTOR, "h2.kp-notebook-searchable")
            author_el = book_el.find_element(By.CSS_SELECTOR, "p.kp-notebook-searchable")
            date_el = book_el.find_element(By.CSS_SELECTOR, "input[id*='kp-notebook-annotated-date']")
            image_el = book_el.find_element(By.CSS_SELECTOR, "img.kp-notebook-cover-image")
            
            title = title_el.text.strip()
            author = author_el.text.replace("By: ", "").strip()
            last_accessed = date_el.get_attribute("value")
            image_url = image_el.get_attribute("src")
            
            book_info[title] = {
                "author": author,
                "last_accessed": last_accessed,
                "image_url": image_url
            }
        except:
            pass
    
    book_titles = list(book_info.keys())
    print(f"Found {len(book_titles)} books to scrape.")

    for i, title in enumerate(book_titles):
        print(f"[{i+1}/{len(book_titles)}] Scraping book: '{title}'")
        highlights_data[title] = {
            "author": book_info[title]["author"],
            "last_accessed": book_info[title]["last_accessed"],
            "image_url": book_info[title]["image_url"],
            "highlights": []
        }
        try:
            # Find the h2 element and click it
            h2_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//h2[contains(text(), '{title[:20]}')]"))
            )
            h2_element.click()
            
            # Wait for the annotation section to load and scroll to it
            try:
                annotation_section = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "annotation-section"))
                )
                # Scroll the annotation section into view to trigger lazy loading
                driver.execute_script("arguments[0].scrollIntoView(true);", annotation_section)
            except:
                pass
            
            # Wait for highlight containers to load (at least one should be present)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.a-row.a-spacing-base span[id='annotationHighlightHeader']"))
            )
            
            # Extract highlights with metadata
            highlight_containers = driver.find_elements(By.CSS_SELECTOR, "div.a-row.a-spacing-base")
            for container in highlight_containers:
                try:
                    # Extract page number and highlight type from metadata
                    metadata_el = container.find_element(By.CSS_SELECTOR, "span[id='annotationHighlightHeader']")
                    metadata_text = metadata_el.text  # e.g., "Yellow highlight | Page: 6"
                    
                    # Parse metadata into components
                    color = None
                    location_type = None
                    location_value = None
                    
                    if "|" in metadata_text:
                        parts = metadata_text.split("|")
                        # Extract color (e.g., "Yellow highlight" -> "Yellow")
                        color_part = parts[0].strip().replace(" highlight", "").strip()
                        color = color_part if color_part else None
                        
                        # Extract location type and value (e.g., "Page: 6" or "Location: 39")
                        location_part = parts[1].strip()
                        if ":" in location_part:
                            loc_type, loc_val = location_part.split(":", 1)
                            location_type = loc_type.strip()
                            location_value = loc_val.strip()
                    
                    # Extract highlight text
                    highlight_text_el = container.find_element(By.CSS_SELECTOR, "span[id='highlight']")
                    highlight_text = highlight_text_el.text.strip()
                    
                    # Try to extract note if it exists
                    note_text = ""
                    try:
                        note_el = container.find_element(By.CSS_SELECTOR, "span[id='note']")
                        note_text = note_el.text.strip()
                    except:
                        pass
                    
                    if highlight_text:
                        highlight_entry = {
                            "text": highlight_text,
                            "color": color,
                            "location_type": location_type,
                            "location": location_value,
                            "note": note_text if note_text else None
                        }
                        highlights_data[title]["highlights"].append(highlight_entry)
                except:
                    pass
            
            print(f"Extracted {len(highlights_data[title]['highlights'])} highlights for '{title}'.")
            
        except Exception as e:
            print(f"Error scraping '{title}': {e}")

    print("Finished scraping all books.")
    return highlights_data


if __name__ == "__main__":
    driver.get(NOTEBOOK_URL) # This line opens the URL
    print(f"Opened {NOTEBOOK_URL}. You have 20 seconds to log in manually if needed.")
    time.sleep(20) # Gives you time to log in if your session expired
    
    highlights = scrape_highlights(driver)
    with open('highlights.json', 'w', encoding='utf-8') as f:
        json.dump(highlights, f, indent=4, ensure_ascii=False)
    print("Highlights saved to highlights.json")
    driver.quit()
