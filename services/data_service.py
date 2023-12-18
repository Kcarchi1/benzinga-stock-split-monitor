import json

import redis


class DataService:
    def __init__(self):
        self.storage = []
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def extend_storage(self, data):
        self.storage.extend(data)

    def clear_storage(self):
        self.storage.clear()

    def set(self):
        self.r.set("split_temp", self._serialize(data=self.storage))

    def get(self):
        return self._deserialize(data=self.r.get("split_temp"))

    def compare(self, past_data):
        return [data for data in self.storage if data not in past_data]
    
    def publish(self, new_data):
        self.r.publish("newsplit_channel", self._serialize(data=new_data))

    def _serialize(self, data):
        return json.dumps(data)

    def _deserialize(self, data):
        if data is None:
            return None
        
        return json.loads(data)


class DataCleaner:
    @staticmethod
    def filter_duplicates(storage):
        temp = {}

        for item in storage:
            if item["ticker"] in temp:
                if DataCleaner.count_na(temp[item["ticker"]]) > DataCleaner.count_na(item): 
                    for key, value in item["info"].items():
                        if value != "N/A":
                            temp[item['ticker']]["info"][key] = value
                continue

            temp[item["ticker"]] = item

        return [value for value in temp.values()]

    @staticmethod
    def count_na(listing):
        return sum(1 for value in listing.get("info").values() if value == "N/A")

