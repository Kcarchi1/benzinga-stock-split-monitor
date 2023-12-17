import logging
import sys
from datetime import datetime

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from .base import BaseSeleniumMonitor


class BenzingaMonitor(BaseSeleniumMonitor):
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    def __init__(self):
        super().__init__(url="https://www.benzinga.com/calendars/stock-splits")
        self.actions = ActionChains(self.driver)
    
    def run(self):
        self.launch_site()
        try:
            parent = self.get_table_body_element()
        except TimeoutException:
            BenzingaMonitor.log.exception("Table element not found")
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
                "info": {
                    "company": listing[1],
                    "ex_date": self._format_date(listing[0]),
                    "exchange": listing[3],
                    "date_announced": self._format_date(listing[5]),
                    "ratio": listing[4]
                }
            }
            standardized_data.append(converted_listing)
        
        return standardized_data
    
    def _format_date(self, date):
        return datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d")


if __name__ == "__main__":
    a = BenzingaMonitor()
    print(a.run())