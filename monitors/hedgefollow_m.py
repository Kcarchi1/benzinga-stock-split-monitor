import sys
import logging

from selenium.common.exceptions import TimeoutException

from .base import BaseSeleniumMonitor


class HedgeFollowMonitor(BaseSeleniumMonitor):
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    def __init__(self):
        super().__init__(url="https://hedgefollow.com/upcoming-stock-splits.php")

    def run(self):
        self.launch_site()
        try:
            parent = self.get_table_body_element()
        except TimeoutException:
            HedgeFollowMonitor.log.exception("Table element not found for HedgeFollow")
            sys.exit(1)
        children = self.get_table_row_elements(parent)
        grandchildren = self.get_data_cell_elements(children)
        self.close_site()
        return self.standardize(grandchildren)

    def standardize(self, listings):
        standardized_data = []
        for listing in listings:
            converted_listing = {
                "ticker": listing[0],
                "info": {
                    "company": listing[2],
                    "ex_date": listing[4],
                    "exchange": listing[1],
                    "date_announced": listing[5],
                    "ratio": listing[3]
                }
            }
            standardized_data.append(converted_listing)
        
        return standardized_data
