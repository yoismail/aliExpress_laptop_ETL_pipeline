import logging
import time
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# logging setup
from etl.logger import setup_logging, section, timed
setup_logging()

# URL to test scraping
ALIEXPRESS_URL = (
    "https://www.aliexpress.com/w/wholesale-laptop.html"
    "?spm=a2g0o.productlist.search.0"
)


@timed
def test_response(url: str) -> bool:
    section("HTTP Response Check")

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/147.0.0.0 Safari/537.36"
                )
            },
            # When request is sent, if no response is received within 15 seconds, it will raise a timeout exception.
            timeout=15,
        )

        if response.status_code == 200:
            logging.info(
                f"Successfully accessed {url} | status={response.status_code}"
            )
            return True

        logging.error(
            f"Failed to access {url} | status={response.status_code}"
        )
        return False

    except Exception as e:
        logging.exception(f"HTTP request failed: {e}")
        return False


@timed
def test_selenium(url: str):  # Changed return type from None → returns driver
    section("Selenium Browser Check")

    # Add Chrome options for headless mode and better compatibility
    options = Options()
    # Open window in maximized mode
    options.add_argument("--start-maximized")
    # Run chrome without opening any visible window (headless mode)
    # options.add_argument("--headless=new")

    """---Disable automation flags to reduce bot detection---"""
    # 1. Hide internal "I'm a robot" flag
    options.add_argument("--disable-blink-features=AutomationControlled")
    # 2. Hide startup command that says "--enable-automation"
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # 3. Remove the hidden automation plugin
    options.add_experimental_option("useAutomationExtension", False)

    driver = None

    try:
        # Use Selenium tool to LAUNCH a real Google Chrome browser on my computer.
        driver = webdriver.Chrome(options=options)

        logging.info(f"Opening page: {url}")
        driver.get(url)

        # CRITICAL: Remove final automation flag (extra protection)
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Tells Selenium: “If you can’t find an element right away, wait up to 8 seconds before giving up.”
        driver.implicitly_wait(8)

        logging.info(f"Page title: {driver.title}")

        # Accept cookies if prompted (common on AliExpress and many sites)
        try:
            accept_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//*[self::button or self::span][contains(., 'Accept') or contains(., 'accept') or contains(., 'Agree')]")
                )
            )
            accept_btn.click()
            logging.info("✅ Cookies accepted automatically")
            time.sleep(2)  # wait for page to reload after accept
        except Exception as cookie_err:
            logging.info(
                f"ℹ️ No cookie button found or already accepted: {cookie_err}")

        # Add a scroll to trigger lazy loading
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # THEN extract
        products = driver.find_elements(By.CSS_SELECTOR, "a[href*='/item/']")

        logging.info(f"Detected {len(products)} product-like elements")

        if products:
            logging.info("Selenium page load looks successful")
        else:
            logging.warning("Page loaded, but no products detected")

    except Exception as e:
        logging.exception(f"Selenium test failed: {e}")
        # If something failed, close driver here before returning None
        if driver:
            driver.quit()
            driver = None

    # Don't quit the driver here, since we want to return it for further use in extraction
    return driver


if __name__ == "__main__":
    if test_response(ALIEXPRESS_URL):
        driver = test_selenium(ALIEXPRESS_URL)
        # Test: if driver exists, close it here
        if driver:
            driver.quit()
            logging.info("✅ Test run done, driver closed")
