import logging
import sys
from datetime import datetime

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class BaseSeleniumScraper():
    def __init__(self, url):
        self.url = url
        self.options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=self.options)

    def launch_site(self):
        self.driver.get(self.url)

    def close_site(self):
        self.driver.quit()

    def get_table_body_element(self):
        return WebDriverWait(driver=self.driver, timeout=5).until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))

    def get_table_row_elements(self, body):
        return body.find_elements(By.TAG_NAME, "tr")
        
    def get_data_cell_elements(self, rows):
        data_cell_list = []
        for row in rows:
            data_cells = row.find_elements(By.TAG_NAME, "td")
            content = [data_cell.text for data_cell in data_cells]

            if len(content) <= 1:
                continue

            data_cell_list.append(self._to_dict(content))

        return data_cell_list
    
    def _to_dict(self, data_list):
        return dict(enumerate(data_list))


class BenzingaScraper(BaseSeleniumScraper):
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    def __init__(self):
        super().__init__(url="https://www.benzinga.com/calendars/stock-splits")
        self.options.add_argument("--disable-notifications")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        self.options.add_experimental_option("useAutomationExtension", False)

        self.actions = ActionChains(self.driver)
    
    def run(self):
        self.launch_site()

        try:
            parent = self.get_table_body_element()
        except TimeoutException:
            BenzingaScraper.log.exception("Table element not found for Benzinga")
            sys.exit(1)

        self._scroll_table(parent)
        children = self.get_table_row_elements(parent)
        grandchildren = self.get_data_cell_elements(children)
        self.close_site()
        
        return self.standardize(grandchildren)

    def _scroll_table(self, table):
        self.actions.send_keys_to_element(table, Keys.PAGE_DOWN).perform()

    def standardize(self, listings):
        standardized_data = []
        for listing in listings:
            converted_listing = {
                "ticker": listing[2],
                "company": listing[1],
                "ex_date": self._format_date(listing[0]),
                "exchange": listing[3],
                "date_announced": self._format_date(listing[5]),
                "ratio": listing[4]
            }
            standardized_data.append(converted_listing)
        
        return standardized_data
    
    def _format_date(self, date):
        return datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d")
