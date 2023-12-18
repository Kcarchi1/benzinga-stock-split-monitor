
import certifi
import json
import logging
import sys

import redis
from pymongo.mongo_client import MongoClient

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

uri = "your_uri"
db_name = "your_db_name"
collection_name = "your_collection_name"
client = MongoClient(uri, tlsCAFile=certifi.where())

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    log.exception(e)
    sys.exit(1)

db = client[db_name]
collection = db[collection_name]


def ticker_exists(ticker):
    query = {"ticker": ticker}
    return collection.count_documents(query) > 0


def post_to_db(data):
    try:
        collection.insert_one(data)
    except Exception as e:
        log.info(f"Failed to write {data['ticker']} db: {e}")
        sys.exit(1)


def listen_to_channel(channel_name):
    redis_client = redis.Redis(host="localhost", port=6379, db=0)

    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel_name)

    for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            for item in data:
                log.info(f"Alert: {item}")
                if not ticker_exists(item["ticker"]):
                    post_to_db(item)
    

if __name__ == "__main__":
    listen_to_channel("your_channel_name")
