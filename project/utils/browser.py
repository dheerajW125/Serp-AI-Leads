from curl_cffi import requests
from curl_cffi.requests.errors import RequestsError
from bs4 import BeautifulSoup
import time
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

logger = logging.getLogger(__name__)


def create_driver():
    """customizing selenium webdriver
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

class Browser:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        }

    def browse(self, url, max_text_length):
        print(f"browsing {url}",flush=True)
        logger.info(f"browsing {url}")
        response = self.session.get(url, verify=False)
        time.sleep(2)
        response.raise_for_status()
        print(f"Status: {response.status_code} {url}")
        logger.info(f"Status: {response.status_code} {url}")
        if response.status_code <= 302:
            content = response.content
        else:
            driver = create_driver()
            driver.get(url)
            time.sleep(10)
            content = driver.page_source
            driver.quit()
        return self.parse(content, max_text_length)

    def parse(self, response_content, max_text_length):
        soup = BeautifulSoup(response_content, features="html.parser")
        texts = []
        for tag in soup.find_all():
            # if tag.name in ["div",
            #                 "a",
            #                 "p",
            #                 "i",
            #                 "icon",
            #                 "img",
            #                 "script",
            #                 "iframe",
            #                 "text",
            #                 "span",
            #                 "li",
            #                 "table",
            #                 "h1",
            #                 "h2",
            #                 "h3",
            #                 "h4",
            #                 "h5",
            #                 "h6",
            #                 "meta",
            #                 "small",
            #                 "strong",
            #                 "summary",
            #                 "td",
            #                 "tr",
            #                 "th"]:
            if tag.name not in ["link", "style", "head", "body", "script"]:
                text_content = soup.get_text(strip=True)
                texts.append(text_content)

        html_text = " ".join(texts)
        if len(html_text) > max_text_length:
            html_text = html_text[0:max_text_length]
            print(f"Warning: Text truncated due to size limit ({max_text_length} characters)")
            logger.warning(f"Warning: Text truncated due to size limit ({max_text_length} characters)")
        return html_text
