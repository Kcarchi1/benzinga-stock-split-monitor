import time
import logging


class MonitorService:
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    def __init__(self, data_service, timeout = 300, monitor_strategy = None):
        self.data_service = data_service
        self.timeout = timeout
        self._monitor_strategy = monitor_strategy
    
    @property
    def monitor_strategy(self):
        return self._monitor_strategy

    @monitor_strategy.setter
    def monitor_strategy(self, monitor_strategy):
        self._monitor_strategy = monitor_strategy

    def run(self):
        if self.monitor_strategy is not None:
            findings = self.monitor_strategy.run()
            self.data_service.extend_storage(findings)
        else:
            raise TypeError("Monitor strategy must be set.")
    
    def sleep(self):
        MonitorService.log.info("Going to sleep...zzz")
        time.sleep(self.timeout)
