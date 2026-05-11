import logging
import re
import time
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from etl.scraper import test_selenium
from etl.logger import setup_logging, section, timed
import datetime

setup_logging()

RAW_CSV = Path("data/aliexpress_laptops.csv")
BASE_URL = "https://www.aliexpress.com/w/wholesale-{query}.html?page={page}"


def create_output_dir():
    section("Output Directory Check")
    RAW_CSV.parent.mkdir(parents=True, exist_ok=True)
    logging.info(f"Output directory ready: {RAW_CSV.parent}")


def wait_for_page(driver) -> bool:
    try:
        # Wait for the product cards to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "search-item-card-wrapper-gallery"))
        )
        return True
    except Exception as e:
        logging.warning(f"⚠️ Page did not load in time: {e}")
        return False


def navigate_to_page(driver, url: str, retries: int = 3) -> bool:
    for attempt in range(1, retries + 1):
        try:
            driver.get(url)
            if wait_for_page(driver):
                return True
            logging.warning(
                f"⚠️ Attempt {attempt}/{retries} — page loaded but no products found")
        except Exception as e:
            logging.warning(f"⚠️ Attempt {attempt}/{retries} failed: {e}")
            time.sleep(2)
    logging.error(f"❌ Failed to load page after {retries} attempts: {url}")
    return False


def validate_lists(data: dict) -> bool:
    lengths = {k: len(v) for k, v in data.items()}
    if len(set(lengths.values())) != 1:
        logging.error(f"❌ List length mismatch: {lengths}")
        return False
    logging.info(
        f"✅ All lists validated — {list(lengths.values())[0]} records each")
    return True


def extract(query: str = "laptop", total_pages: int = 10) -> pd.DataFrame | None:
    section("Starting Extraction Process")

    driver = test_selenium(BASE_URL.format(query=query, page=1))
    if not driver:
        logging.error("❌ No driver received — stopping extraction")
        return None

    if not wait_for_page(driver):
        logging.error("❌ First page failed to load — stopping extraction")
        driver.quit()
        return None

    # Lists to hold extracted data
    product_names = []
    product_prices = []
    was_prices = []
    discount_infos = []
    extra_discounts = []
    shipping_statuses = []
    total_sold_counts = []
    top_selling_statuses = []

    section("Extracting Product Data")
    for page_num in range(1, total_pages + 1):
        logging.info(f"Processing page {page_num}/{total_pages}")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        laptops = soup.find_all(
            "div", class_="j5_b7 search-item-card-wrapper-gallery")

        if not laptops:
            logging.warning(
                "⚠️ No products found — blocked or selectors outdated")
            break

        logging.info(f"Found {len(laptops)} products on page {page_num}")

        for laptop in laptops:

            # Product name
            name_tag = laptop.find("div", class_="lj_aj")
            product_names.append(name_tag.text.strip() if name_tag else "N/A")

            # Product price
            price_div = laptop.find("div", class_="lj_lf")
            product_prices.append(
                float(re.sub(r'[^\d.]', '', ''.join(
                    s.get_text() for s in price_div.find_all('span'))))
                if price_div else None
            )

            # Was price (crossed-out)
            was_tag = laptop.find(
                "span", style=lambda s: s and "line-through" in s)
            was_prices.append(
                float(re.sub(r'[^\d.]', '', was_tag.get_text().strip()))
                if was_tag else None
            )

            # Discount info
            disc_tag = laptop.find("span", class_="lj_l7")
            discount_infos.append(disc_tag.text.strip()
                                  if disc_tag else "Not discounted")

            # Extra discount
            extra_tag = laptop.find("span", class_="nc_a4 nc_nf")
            extra_discounts.append(extra_tag.text.strip()
                                   if extra_tag else "No extra discount")

            # Shipping status
            ship_tag = laptop.find(
                "span", class_="nc_a4 nc_nf", title="Free shipping")
            shipping_statuses.append(
                ship_tag.text.strip() if ship_tag else "No free shipping")

            # Total sold
            sold_tag = laptop.find("span", class_="lj_j9")
            total_sold_counts.append(
                int(re.sub(r'[^\d]', '', sold_tag.text.strip())
                    ) if sold_tag else 0
            )

            # Top selling status
            top_tag = laptop.find("span", class_="nc_nf",
                                  title="Top selling on AliExpress")
            top_selling_statuses.append(
                top_tag.text.strip() if top_tag else "Not top selling")

        # Navigate to next page
        if page_num < total_pages:
            next_url = BASE_URL.format(query=query, page=page_num + 1)
            if not navigate_to_page(driver, next_url):
                logging.error(
                    f"❌ Stopping at page {page_num} — navigation failed")
                break

    driver.quit()

    # Build and validate
    data = {
        "product_name":        product_names,
        "product_price":       product_prices,
        "was_price":           was_prices,
        "discount_info":       discount_infos,
        "extra_discount":      extra_discounts,
        "shipping_status":     shipping_statuses,
        "total_sold_count":    total_sold_counts,
        "top_selling_status":  top_selling_statuses,
        "scraped_at":         [datetime.datetime.now()] * len(product_names)

    }

    if not validate_lists(data):
        return None

    df = pd.DataFrame(data)
    logging.info(f"✅ Extraction complete — {len(df)} products extracted")
    return df


@timed
def main() -> pd.DataFrame | None:
    create_output_dir()

    df = extract(query="laptop", total_pages=60)

    if df is not None:
        df.to_csv(RAW_CSV, index=False)
        logging.info(f"✅ Raw data saved to {RAW_CSV}")
        return df

    logging.error("❌ Extraction failed — nothing saved")
    return None


if __name__ == "__main__":
    main()
