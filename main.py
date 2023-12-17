import json
import time
import redis
from pprint import pprint

from monitors import BenzingaMonitor, HedgeFollowMonitor, StockAnalysisMonitor
from monitorservice import MonitorService

monitors = [
    BenzingaMonitor, 
    HedgeFollowMonitor, 
    StockAnalysisMonitor,
]

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def main():
    service = MonitorService()

    # while True:
    for monitor_class in monitors:
        monitor = monitor_class()
        service.monitor_strategy = monitor
        service.run()

    pprint(service.storage)
    print(len(service.storage))
    service.filter_duplicates()
    print("to")
    print(len(service.storage))
    # with open("output.json", "w") as f:
    #     json.dump(service.storage, f)
    # service.sleep()
    start_time = time.time()
    sample = json.dumps(service.storage)
    print (f"JSON Dumps:{time.time() - start_time}")
    r.set('foo', sample)
    s = r.get('foo')
    start_time = time.time()
    _ = json.loads(s)
    print(f"JSON Loads:{time.time() - start_time}")
    print(_)
    print(type(_))

if __name__ == "__main__":
    main()