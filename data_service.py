import json

import redis


class DataService:
    def __init__(self):
        self.storage = []
        self.redis = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)

    def extend_storage(self, data):
        self.storage.extend(data)

    def clear_storage(self):
        self.storage.clear()

    def set(self):
        self.redis.set("benzinga_temp", self._serialize(data=self.storage))

    def get(self):
        return self._deserialize(data=self.redis.get("split_temp"))

    def compare(self, past_data):
        return [data for data in self.storage if data not in past_data]
    
    def publish(self, new_data):
        self.redis.publish("rsplits_channel", self._serialize(data=new_data))

    def _serialize(self, data):
        return json.dumps(data)

    def _deserialize(self, data):
        if data is None:
            return None
        
        return json.loads(data)
