import json
import logging
from datetime import datetime

from .base import BaseRequestsMonitor


class StockAnalysisMonitor(BaseRequestsMonitor):
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    def __init__(self):
        super().__init__(url="https://stockanalysis.com/api/actions/splits/2023")
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/119.0.0.0 Safari/537.36",
        })

    def run(self):
        response = self.session.get(url=self.url)
        listings = json.loads(response.content)
        return self.standardize(listings["data"]["data"])
    
    def standardize(self, listings):
        standardized_data = []
        for listing in listings:
            converted_listing = {
                "ticker": self._format_text(listing["symbol"], "$", ""),
                "info": {
                    "company": listing["name"],
                    "ex_date": self._format_date(listing["date"]),
                    "exchange": "N/A",  # Doesn't exist for this data
                    "date_announced": "N/A",  # Doesn't exist for this data
                    "ratio": self._format_text(listing["splitRatio"], " for ", ":")
                }
            }
            standardized_data.append(converted_listing)

        return standardized_data
    
    def _format_text(self, text, old_value, new_value):
        return text.replace(old_value, new_value)

    def _format_date(self, date):
        return datetime.strptime(date, "%b %d, %Y").strftime("%Y-%m-%d")
