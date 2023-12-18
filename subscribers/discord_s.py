import time
import json
import logging
import sys
from typing import Union
from datetime import datetime

import requests
import redis

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

WEBHOOK_URL = "your_webhook_url"
WEBHOOK_DELAY = 2  


def format_webhook( 
        name: str, 
        ticker: str, 
        ratio: str, 
        market: str, 
        ex_date: str, 
        announcement_date: str
    ) -> dict[str, Union[None, list, str]]:
            return {
                "content": None,
                "embeds": [{
                    "title": "Split Detected :chart_with_upwards_trend:",
                    "color": 662854,
                    "fields": [
                        {
                            "name": "Name",
                            "value": name,
                            "inline": True
                        },
                        {
                            "name": "Ticker",
                            "value": ticker,
                            "inline": True
                        },
                        {
                            "name": "Ratio",
                            "value": ratio,
                            "inline": True
                        },
                        {
                            "name": "Market",
                            "value": market,
                            "inline": True
                        },
                        {
                            "name": "Ex-Date",
                            "value": ex_date,
                            "inline": True
                        },
                        {
                            "name": "Date Announced",
                            "value": announcement_date,
                            "inline": True
                        },
                        {
                            "name": "Links",
                            "value": f"Google:\nhttps://www.google.com/search?q={ticker}+stock+split\nEdgar:\n" \
                                    f"https://www.sec.gov/edgar/search/#/q=%2522fractional%2520shares%2522&entityName={ticker}"
                        }
                    ],
                    "footer": {
                        "text": f"Stock Split Monitor • {datetime.now().strftime('%x %I:%M %p')}",
                        "icon_url": "https://www.benzinga.com/next-assets/images/schema-image-default.png"
                    },
                    "thumbnail": {
                        "url": "https://i1.sndcdn.com/artworks-000630740329-qqgqe8-t500x500.jpg"
                    }
                }],
                "username": "Stock Split Monitor",
                "avatar_url": "https://www.benzinga.com/next-assets/images/schema-image-default.png"
            }


def post_to_webhook(
        name: str, 
        ticker: str,
        ratio: str, 
        market: str, 
        ex_date: str, 
        announcement_date: str
    ) -> None:
        time.sleep(WEBHOOK_DELAY)
        try:
            requests.post(
                url=WEBHOOK_URL, 
                json=format_webhook(
                    name=name, 
                    ticker=ticker, 
                    ratio=ratio,
                    market=market, 
                    ex_date=ex_date,
                    announcement_date=announcement_date
                )
            )
        except Exception as e:
            log.exception(f"Failed to post {ticker} to webhook: {e}")
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
                post_to_webhook(
                      name=item["info"]["company"],
                      ticker=item["ticker"],
                      ratio=item["info"]["ratio"],
                      market=item["info"]["exchange"],
                      ex_date=item["info"]["ex_date"],
                      announcement_date=item["info"]["date_announced"]
                )
    

if __name__ == "__main__":
    listen_to_channel("your_channel_name")