from monitors import BenzingaMonitor, HedgeFollowMonitor, StockAnalysisMonitor
from monitorservice import MonitorService

monitors = [
    BenzingaMonitor, 
    HedgeFollowMonitor, 
    StockAnalysisMonitor,
]


def main():
    service = MonitorService()

    # while True:
    for monitor_class in monitors:
        monitor = monitor_class()
        service.monitor_strategy = monitor
        service.run()


if __name__ == "__main__":
    main()
    