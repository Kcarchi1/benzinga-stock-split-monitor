import json
import logging

import redis
from twilio.rest import Client

account_sid = 'your_account_sid'  
auth_token = 'your_auth_token'  
twilio_client = Client(account_sid, auth_token)

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


def send_twilio_message(item):
    try:
        message = twilio_client.messages.create(
            body=f"Stock{item['ticker']}",  
            from_="your_twilio_number",  
            to="recipient_number"  
        )
        log.info(f"Message sent: {message.sid}")
    except Exception as e:
        log.error(f"Failed to send message: {e}")


def listen_to_channel(channel_name):
    redis_client = redis.Redis(host="localhost", port=6379, db=0)

    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel_name)

    for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            for item in data:
                send_twilio_message(item)


if __name__ == "__main__":
    listen_to_channel("your_channel_name")
