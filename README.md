<div align="center">

![Banner](https://capsule-render.vercel.app/api?type=waving&height=300&color=7b4397&text=CM_Scraper&section=header&fontColor=FFFFFF)

# Cardmarket Yu-Gi-Oh! Singles Scraper

<p align="center">A Python scraper to extract Yu-Gi-Oh! singles data (name, expansion, rarity, condition, language, price, amount, comments, image URL, and product URL) from a Cardmarket user's profile. The scraper handles pagination, random delays to avoid rate-limiting, and resumes from previous runs based on expansions already visited.</p>

</div>

## ⚙️ **Tech Stack**

<table align="center">
  <tr>
    <td align="center" width="96">
      <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg" width="48" height="48" alt="Python"/>
      <br>Python
    </td>
    <td align="center" width="96">
      <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/selenium/selenium-original.svg" width="48" height="48" alt="Selenium"/>
      <br>Selenium
    </td>
    <td align="center" width="96">
      <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/pandas/pandas-original-wordmark.svg" width="48" height="48" alt="Pandas"/>
      <br>Pandas
    </td>
  </tr>
</table>

---

## 📌 **Features**

- **Headless Firefox Browser**: Uses Selenium with a headless Firefox browser to scrape data.
- **Pagination Handling**: Automatically navigates through all pages of a user's singles.
- **Random Delays**: Implements random delays between requests to mimic human behavior and avoid detection.
- **Resume Support**: Tracks already scraped expansions to avoid redundant work.
- **CSV Output**: Saves scraped data to CSV files for easy analysis.
- **Error Handling**: Robust error handling for timeouts, missing elements, and other common scraping issues.

---

## 🚀 **Installation**

### **Prerequisites**

- Python 3.8+
- [Firefox](https://www.mozilla.org/firefox/) (for Selenium WebDriver)

### **Dependencies**

Install the required packages using pip:

```bash
pip install selenium webdriver-manager pandas
```

---

## 📝 **Usage**

### **Command Line Arguments**

<div align="center">

| Argument       | Description                                      | Default Value               |
| -------------- | ------------------------------------------------ | --------------------------- |
| `user_id`      | Cardmarket user ID                               | **Required**                |
| `--output`     | Output CSV filename for cards                    | `cardmarket_cards.csv`      |
| `--expansions` | Output CSV filename for expansions               | `cardmarket_expansions.csv` |

<div/>

### **Run the Scraper**

```bash
python cardmarket_scraper.py <user_id> [--output <output_file>] [--expansions <expansions_file>]
```

**Example:**

```bash
python cardmarket_scraper.py username --output date_username_cards.csv --expansions date_username_expansions.csv
```

---

### **Output Files**

- `**<output_file>.csv**`: Contains all scraped cards with the following columns:
  - `name`
  - `expansion`
  - `expansion_name`
  - `rarity`
  - `condition`
  - `language`
  - `price`
  - `amount`
  - `comments`
  - `image_url`
  - `product_url`

- `**<expansions_file>.csv**`: Tracks which expansions have already been scraped to support resuming.

---

### **Code Structure**

<div align="center">

| Function                           | Description                                                      |
| ---------------------------------- | ---------------------------------------------------------------- |
| `setup_driver()`                   | Configures a headless Firefox browser with human-like settings.  |
| `get_expansion_options()`          | Extracts all expansion options from the filter dropdown.         |
| `get_number_of_singles()`          | Fetches the total number of singles available for a user.        |
| `scrape_page()`                    | Scrapes all cards from the current page.                         |
| `scrape_expansion()`               | Scrapes all cards for a specific expansion, handling pagination. |
| `scrape_all_expansions_for_user()` | Scrapes all expansions for a user, resuming from previous runs.  |
| `save_to_csv()`                    | Saves scraped cards to a CSV file.                               |
| `save_expansion_to_csv()`          | Saves scraped expansions to a CSV file.                          |

<div/>

---

## 💡 **Notes**

- **Rate Limiting**: The scraper uses random delays (`random_delay()`) to avoid triggering anti-bot measures.
- **Resuming**: If the scraper is interrupted, it will resume from the last scraped expansion.
- **Error Handling**: The scraper logs errors and continues to the next page/expansion if an issue occurs.

---

## 📄 **License**

<div align="center">

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

</div>

---

## 🌟 **Contribute & Feedback**

Contributions are welcome! Open an issue or submit a pull request for any improvements or bug fixes.

---

## 🙏 **Acknowledgments**

- [Selenium](https://www.selenium.dev/)
- [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager)
- [Pandas](https://pandas.pydata.org/)
- [Le Chat](https://chat.mistral.ai/chat)

<div align="center">

![Banner](https://capsule-render.vercel.app/api?type=waving&height=150&color=7b4397&section=footer&fontColor=FFFFFF)

</div>
