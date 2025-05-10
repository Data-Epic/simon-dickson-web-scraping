import logging
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config import FBREF_URL

class FBRefClient:
    """I handled web scraping from FBRef using Selenium and BeautifulSoup.

    I initialized with a URL (defaulting to FBREF_URL from config) and set up a user agent
    to mimic a browser. I then provided methods to fetch HTML content and parse it into a
    BeautifulSoup object, handling Cloudflare challenges with retries.
    """
    def __init__(self, url=FBREF_URL):
        """I initialized the FBRefClient with a target URL and user agent.

        Args:
            url (str, optional): The URL to scrape. Defaults to FBREF_URL from config.
        """
        self.url = url
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        )

    def fetch_html(self, retries=3, delay=5):
        """To fetch the HTML content from the target URL using Selenium.

        I configured a headless Chrome browser, visit the FBRef homepage to establish a session,
        then navigate to the target URL. I handle Cloudflare challenges by retrying up to the
        specified number of times with a delay between attempts. I cleaned the HTML by removing
        HTML comment tags before returning it.

        Args:
            retries (int, optional): Number of retry attempts. Defaults to 3.
            delay (int, optional): Delay between retries in seconds. Defaults to 5.

        Returns:
            str: The cleaned HTML content of the page.

        Raises:
            Exception: If all retries fail to resolve the Cloudflare challenge.
        """
        logging.info(f"Fetching FBRef page: {self.url}")
        homepage = "https://fbref.com/en/"

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={self.user_agent}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        for attempt in range(retries):
            driver = None
            try:
                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=chrome_options
                )
                driver.get(homepage)
                time.sleep(2)
                driver.get(self.url)
                time.sleep(5)
                if "Just a moment" in driver.title:
                    logging.error(f"Attempt {attempt + 1} blocked by Cloudflare.")
                    raise Exception("Cloudflare challenge not resolved")
                html = driver.page_source
                logging.info("Page fetched successfully with Selenium.")
                return html.replace("<!--", "").replace("-->", "")
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    logging.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logging.error("Max retries reached. Failed to fetch page.")
                    raise
            finally:
                if driver:
                    driver.quit()

    def get_soup(self):
        """I fetched the HTML content and parse it into a BeautifulSoup object.

        Returns:
            BeautifulSoup: The parsed HTML content as a BeautifulSoup object.
        """
        html = self.fetch_html()
        return BeautifulSoup(html, "lxml")