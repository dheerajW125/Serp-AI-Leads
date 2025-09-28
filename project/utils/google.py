import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


def get_base_url(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"    
    return base_url

class GoogleSearch:
    search_url = "https://www.google.com/search"

    def __init__(self, proxy) -> None:
        self.session = requests.Session()
        self.session.verify = False
        self.session.proxies["https"] = proxy

        retry_strategy = Retry(3, backoff_factor=2, status_forcelist=[500, 502])
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        urllib3.disable_warnings()

    def search(self, keyword, page=1):
        print(f"searching for keyword:{keyword} on page:{page}")
        logger.info(f"searching for keyword:{keyword} on page:{page}")

        params = {"q": keyword, "brd_json": 1, "gl": "us", "start": (page - 1) * 20}
        response = self.session.get(self.search_url, params=params)
        response.raise_for_status()
        return self.parse(response.json())

    def parse(self, response_json):
        results = response_json.get("organic", [])

        links = [get_base_url(result["link"]) for result in results]
        return links
