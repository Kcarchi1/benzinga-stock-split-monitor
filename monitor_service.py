import time
import logging


class MonitorService:
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    def __init__(self, data_service, timeout = 300, scraper_strategy = None):
        self.data_service = data_service
        self.timeout = timeout
        self._scraper_strategy = scraper_strategy
    
    @property
    def scraper_strategy(self):
        return self._scraper_strategy

    @scraper_strategy.setter
    def scraper_strategy(self, scraper_strategy):
        self._scraper_strategy = scraper_strategy

    def run(self):
        if self.scraper_strategy is not None:
            findings = self.scraper_strategy.run()
            self.data_service.extend_storage(findings)
        else:
            raise TypeError("Monitor strategy must be set.")
    
    def sleep(self):
        MonitorService.log.info("Going to sleep...zzz")
        time.sleep(self.timeout)
