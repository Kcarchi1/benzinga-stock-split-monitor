from monitors import BenzingaMonitor, HedgeFollowMonitor, StockAnalysisMonitor
from services import MonitorService, DataService, DataCleaner

monitors = [
    BenzingaMonitor, 
    HedgeFollowMonitor, 
    StockAnalysisMonitor,
]


def main():
    service = MonitorService(DataService(), timeout=30)

    while True:
        MonitorService.log.info("Running Monitor...")

        for monitor_class in monitors:
            monitor = monitor_class()
            service.monitor_strategy = monitor
            service.run()
        
        service.data_service.storage = DataCleaner.filter_duplicates(service.data_service.storage)

        """
        Grab past data in redis
        if none, then data is empty, so push current data to fill
        else, compare past data with current data
        publish new 
        overwrite past data with current data
        """
        past_data = service.data_service.get()
        if past_data is None:
            MonitorService.log.info("Previous data not present. Setting current data...")
            service.data_service.set()
        else:
            new_data = service.data_service.compare(past_data)

            if not new_data:
                MonitorService.log.info("No changes detected")
            else:
                MonitorService.log.info(f"Publishing new splits:\n{new_data}")
                service.data_service.publish(new_data)
                service.data_service.set()

        service.data_service.clear_storage()
        service.sleep()


if __name__ == "__main__":
    main()
    