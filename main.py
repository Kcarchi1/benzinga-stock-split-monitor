from scrapers import BenzingaScraper
from monitor_service import MonitorService
from data_service import DataService

CONNECT_TIMEOUT = 20
READ_TIMEOUT = 20


def main():
    service = MonitorService(DataService())

    MonitorService.log.info("Running Monitor...")
    while True:
        scraper = BenzingaScraper()
        service.scraper_strategy = scraper
        service.run()
        
        past_data = service.data_service.get()
        if past_data is None:
            MonitorService.log.info("Previous data not present. Setting current data...")
            print(service.data_service.storage)
            service.data_service.set()
        else:
            new_data = service.data_service.compare(past_data)

            if not new_data:
                MonitorService.log.info("No changes detected")
            else:
                for data in new_data:
                    MonitorService.log.info(f"New press release: {data['heading']}")
                MonitorService.log.info("Publishing new data...")
                service.data_service.publish(new_data)
                service.data_service.set()

        service.data_service.clear_storage()
        service.sleep()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # post_to_webhook()
        raise e