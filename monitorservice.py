import time
import logging


class MonitorService:
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    def __init__(self, timeout = 300, monitor_strategy = None):
        self.timeout = timeout
        self._monitor_strategy = monitor_strategy
        self.storage = []
    
    @property
    def monitor_strategy(self):
        return self._monitor_strategy

    @monitor_strategy.setter
    def monitor_strategy(self, monitor_strategy):
        self._monitor_strategy = monitor_strategy

    def run(self):
        if self.monitor_strategy is not None:
            findings = self.monitor_strategy.run()
            self._extend_storage(findings)
        else:
            raise TypeError("Monitor strategy must be set.")
    
    def filter_duplicates(self):
        temp = {}

        for item in self.storage:
            if item["ticker"] in temp:
                if self.count_na(temp[item["ticker"]]) > self.count_na(item): 
                    for key, value in item["info"].items():
                        if value != "N/A":
                            temp[item['ticker']]["info"][key] = value
                
                continue

            temp[item["ticker"]] = item

        self.storage = [value for value in temp.values()]

    def count_na(self, listing):
        return sum(1 for value in listing.get("info").values() if value == "N/A")

    def sleep(self):
        MonitorService.log.info("Going to sleep...zzz")
        time.sleep(self.timeout)

    def clear_storage(self):
        self.storage.clear()

    def _extend_storage(self, response):
        self.storage.extend(response)

