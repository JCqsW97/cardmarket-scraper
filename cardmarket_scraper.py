from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import argparse
import os
import json
import random
import re
from urllib.parse import urljoin

BASE_URL = "https://www.cardmarket.com"

def random_delay(min_sec=1, max_sec=3):
    """Wait for a random delay."""
    time.sleep(random.uniform(min_sec, max_sec))

def setup_driver():
    """Set up a headless Firefox browser with human-like configurations."""
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--disable-gpu")
    firefox_options.add_argument("--window-size=1920,1080")
    firefox_options.add_argument("--lang=en-US")
    firefox_options.set_preference(
        "general.useragent.override",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
    )
    driver = webdriver.Firefox(
        service=Service(GeckoDriverManager().install()),
        options=firefox_options
    )
    return driver

def get_expansion_options(driver, user_id):
    """Extract all expansion options from the filter dropdown."""
    url = f"{BASE_URL}/en/YuGiOh/Users/{user_id}/Offers/Singles"
    driver.get(url)
    time.sleep(random.uniform(3, 6))

    try:
        wait = WebDriverWait(driver, 20)
        filter_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-component-name='CategoryOffersFilterComponent']"))
        )
        props = filter_element.get_attribute("data-props")
        if not props:
            print("No data-props found.")
            return []

        # Parse expansion options from data-props
        json_match = re.search(r'"expansionOptions":\s*(\[.*?\])', props, re.DOTALL)
        if not json_match:
            print("No expansionOptions found.")
            return []

        expansions_json = json_match.group(1)
        expansions_json = expansions_json.replace('\\"', '"')
        expansions = json.loads(expansions_json)
        return [{"label": exp["label"], "value": exp["value"]} for exp in expansions if exp["value"] != "0"]  # Exclude "All"
    except Exception as e:
        print(f"Error getting expansion options: {e}")
        return []

def get_number_of_singles(driver, user_id):
    """Extract the number of singles available for a given user."""
    url = f"{BASE_URL}/en/YuGiOh/Users/{user_id}/Offers"
    driver.get(url)
    time.sleep(random.uniform(3, 6))

    try:
        wait = WebDriverWait(driver, 20)
        # Find the Singles card and then the div with the number
        singles_card = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/Offers/Singles']"))
        )
        nb_singles = singles_card.find_element(By.CSS_SELECTOR, ".bracketed.text-muted.small.mt-1").text.strip('()')
        print(f"\nNumber of cards for this user: {nb_singles}")
        if not nb_singles:
            print("No number of singles found.")
            return None
        return int(nb_singles)
    except Exception as e:
        print(f"Error getting number of singles: {e}")
        return None

def scrape_page(driver):
    """Scrape all cards from the current page."""
    cards = []
    try:
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".article-row")))
        rows = driver.find_elements(By.CSS_SELECTOR, ".article-row")
        for row in rows:
            try:
                # Extract name
                name = row.find_element(By.CSS_SELECTOR, ".col-seller a").text.strip()

                # Extract expansion and expansion_name
                expansion_elem = row.find_element(By.CSS_SELECTOR, ".expansion-symbol")
                expansion = expansion_elem.text.strip()
                expansion_name = expansion_elem.get_attribute("data-bs-original-title")

                # Extract rarity (fallback to "Unknown" if not found)
                rarity_language_elems = row.find_elements(By.CSS_SELECTOR, ".me-2")
                rarity = rarity_language_elems[1].get_attribute("data-bs-original-title") if rarity_language_elems else "Unknown"

                # Extract condition
                condition = row.find_element(By.CSS_SELECTOR, ".article-condition").text.strip()

                # Extract language (fallback to "Unknown" if not found)
                language = rarity_language_elems[2].get_attribute("data-bs-original-title") if rarity_language_elems else "Unknown"

                # Extract price
                price = row.find_element(By.CSS_SELECTOR, ".price-container").text.strip().replace("\xa0", " ")

                # Extract amount
                amount = driver.execute_script('return arguments[0].querySelector(".item-count")?.textContent.trim() || "0";', row)

                # Extract comments (fallback to empty string if not found)
                comment_elems = row.find_elements(By.CSS_SELECTOR, ".product-comments")
                comments = comment_elems[0].text.strip() if comment_elems else ""

                # Extract image URL
                image_url_elem = row.find_element(By.CSS_SELECTOR, ".thumbnail-icon")
                image_url = image_url_elem.get_attribute("data-bs-title").split('"')[1]

                # Extract product URL
                product_url = urljoin(BASE_URL, row.find_element(By.CSS_SELECTOR, ".col-seller a").get_attribute("href"))

                card = {
                    "name": name,
                    "expansion": expansion,
                    "expansion_name": expansion_name,
                    "rarity": rarity,
                    "condition": condition,
                    "language": language,
                    "price": price,
                    "amount": amount,
                    "comments": comments,
                    "image_url": image_url,
                    "product_url": product_url,
                }
                cards.append(card)
            except Exception as e:
                print(f"    Error parsing row: {e}")
                continue
    except TimeoutException:
        print("    No cards found on this page (timeout).")
        return []
    except NoSuchElementException:
        print("    No cards found on this page (no such element).")
        return []
    except Exception as e:
        print(f"    Error scraping page: {e}")
        return []
    return cards

def has_next_page(driver):
    """Check if there is a next page."""
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "a[data-direction='next']:not(.disabled)")
        return next_button is not None
    except NoSuchElementException:
        return False

def go_to_next_page(driver):
    """Click the next page button."""
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "a[data-direction='next']:not(.disabled)")
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(random.uniform(3, 6))  # Wait for page to load
    except Exception as e:
        print(f"Error going to next page: {e}")

def scrape_expansion(driver, user_id, expansion_id, expansion_name):
    """Scrape all cards for a specific expansion, handling pagination."""
    url = f"{BASE_URL}/en/YuGiOh/Users/{user_id}/Offers/Singles?idExpansion={expansion_id}"
    driver.get(url)
    random_delay(5, 8)
    random_delay(2, 11)

    all_cards = []
    page = 1
    cards = scrape_page(driver)
    if not cards:
        print(f"    No cards in expansion: {expansion_name}.")
        return all_cards
    all_cards.extend(cards)
    print(f"    Found {len(cards)} cards on page {page}.")

    while has_next_page(driver):
        random_delay(1, 3)
        go_to_next_page(driver)
        page += 1
        print(f" -> Scraping {expansion_name} (Page {page})...")
        cards = scrape_page(driver)
        if not cards:
            print(f"    No cards found for {expansion_name} (Page {page}).")
            break
        all_cards.extend(cards)
        print(f"    Found {len(cards)} cards on page {page}.")

    return all_cards

def get_scraped_expansions(filename):
    """Return a set of expansion IDs already in the CSV."""
    if not os.path.exists(filename):
        return set()
    df = pd.read_csv(filename)
    return set(df["expansion_name"].unique())

def scrape_all_expansions_for_user(driver, user_id, output_file, expansion_file):
    expansions = get_expansion_options(driver, user_id)
    singles_number = get_number_of_singles(driver, user_id)
    cards_already_scraped_number = sum_eighth_column(output_file)
    if not expansions:
        print("No expansions found. Trying to scrape without expansion filter...")
        cards = scrape_expansion(driver, user_id, None, "All")
        save_to_csv(cards, output_file)
        return cards

    # Get already scraped expansions
    scraped_expansions = get_scraped_expansions(expansion_file)
    print(f"\nFound {len(expansions)} expansions for user {user_id}.")
    if {len(expansions)} == {len(scraped_expansions)}:
        print ("\nAll expansions have already been scraped.")
        return
    else:
        print(f"\nAlready scraped {len(scraped_expansions)} expansions. Resuming...")

    all_cards = []
    total_expansions = len(expansions)
    for i, expansion in enumerate(expansions, 1):
        expansion_id = expansion["value"]
        expansion_name = expansion["label"]
        print(f"\n[{i}/{total_expansions}] Current expansion: {expansion_name} (ID: {expansion_id})")
        current_expansion = [{"expansion_name": expansion_name,}]

        print(f"    [{cards_already_scraped_number + len(all_cards)}/{singles_number}] Cards already scraped")

        if singles_number == (len(all_cards) + cards_already_scraped_number):
            print(f" ** All cards have already been scraped")
            return all_cards
        
        if expansion_name in scraped_expansions:
            print(f" -  Skipping already scraped expansion: {expansion_name} (ID: {expansion_id})")
            continue
        print(f" -> Scraping expansion: {expansion_name} (ID: {expansion_id})...")

        cards = scrape_expansion(driver, user_id, expansion_id, expansion_name)

        if cards:
            all_cards.extend(cards)
            save_to_csv(cards, output_file, append=True)
        
        save_expansion_to_csv(current_expansion, expansion_file, append=True)

    return all_cards

def sum_eighth_column(filename):
    """Return the sum of the values in the eighth column (H) of a CSV file."""
    if not os.path.exists(filename):
        return 0
    df = pd.read_csv(filename)
    eighth_column = df.iloc[:, 7]
    return eighth_column.sum()


def save_to_csv(cards, filename, append=False):
    """Save the scraped cards to a CSV file, optionally appending."""
    try:
        if not cards:
            print("No cards to save.")
            return
        df = pd.DataFrame(cards)
        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
        mode = 'a' if append and os.path.exists(filename) else 'w'
        header = not append or not os.path.exists(filename)
        df.to_csv(filename, index=False, encoding="utf-8-sig", mode=mode, header=header)
        print(f" *  Saved {len(cards)} cards to {filename} (append={append})")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def save_expansion_to_csv(expansions, filename, append=False):
    """Save the expansions to a CSV file, optionally appending."""
    try:
        if not expansions:
            print("No expansions to save.")
            return
        df = pd.DataFrame(expansions)
        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
        mode = 'a' if append and os.path.exists(filename) else 'w'
        header = not append or not os.path.exists(filename)
        df.to_csv(filename, index=False, encoding="utf-8-sig", mode=mode, header=header)
        print(f" *  Saved {len(expansions)} expansions to {filename} (append={append})")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(description="Scrape Cardmarket user's singles using Firefox.")
    parser.add_argument("user_id", type=str, help="Cardmarket user ID (e.g., 'Sahora')")
    parser.add_argument("--output", type=str, default="cardmarket_cards.csv", help="Output CSV filename")
    parser.add_argument("--expansions", type=str, default="cardmarket_expansions.csv", help="Output Expansions filename")
    args = parser.parse_args()

    print(f"\nScraping all cards for user: {args.user_id}...")
    driver = setup_driver()
    try:
        cards = scrape_all_expansions_for_user(driver, args.user_id, args.output, args.expansions)
    finally:
        driver.quit()
    print("\nScraping is done.")

    end_time = time.time()
    runtime = end_time - start_time
    hours = int(runtime // 3600)
    minutes = int((runtime % 3600) // 60)
    seconds = runtime % 60

    print(f"Scraper ran for {hours}h {minutes}m {seconds:.2f}s")

if __name__ == "__main__":
    main()