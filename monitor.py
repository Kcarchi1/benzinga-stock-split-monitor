import logging
import time
from datetime import datetime
from typing import Union

import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

DELAY_TIME = 600 

WEBHOOK_URL = "CHANGE ME"

WEBHOOK_DELAY = 2

OPTIONS = webdriver.ChromeOptions()
OPTIONS.add_argument("--disable-notifications")
OPTIONS.add_argument("--disable-blink-features=AutomationControlled")
OPTIONS.add_experimental_option("excludeSwitches", ["enable-automation"]) 
OPTIONS.add_experimental_option("useAutomationExtension", False) 


def grab_splits(filename: str) -> dict[str, str]:
    try:
        splits = {}
        with open(filename, "r") as f:
            lines = f.readlines()
            for line in lines:
                key, value = line.strip().split("@")
                splits[key] = value

        return splits
    except FileNotFoundError:
        open(filename, "w").close()
        return grab_splits(filename)


def format_webhook(ticker: str, ratio: str) -> dict[str, Union[None, list, str]]:
    return {
        "content": None,
        "embeds": [{
            "title": "Split Detected :chart_with_upwards_trend:",
            "color": 662854,
            "fields": [
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
                "name": "Ex. Date",
                "value": "test",
                "inline": True
                },
                {
                "name": "Links",
                "value": f"Google:\nhttps://www.google.com/search?q={ticker}+stock+split\nEdgar:\nhttps://www.sec.gov/edgar/search/#/q=%2522fractional%2520shares%2522&entityName={ticker}"
                }
            ],
            "footer": {
                "text": f"Benzinga Monitor • {datetime.now().strftime('%x %I:%M %p')}",
                "icon_url": "https://www.benzinga.com/next-assets/images/schema-image-default.png"
            },
            "thumbnail": {
                "url": "https://i1.sndcdn.com/artworks-000630740329-qqgqe8-t500x500.jpg"
            }
        }],
        "username": "Benzinga Monitor",
        "avatar_url": "https://www.benzinga.com/next-assets/images/schema-image-default.png"
    }


def post_to_webhook(ticker: str, ratio: str) -> None:
    time.sleep(WEBHOOK_DELAY)
    requests.post(url=WEBHOOK_URL, json=format_webhook(ticker=ticker, ratio=ratio))


def main():
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    
    while True:
        log.info("Running Benzinga Monitor...")

        driver = webdriver.Chrome(options=OPTIONS)
        driver.get("https://www.benzinga.com/calendars/stock-splits")

        parent = WebDriverWait(driver=driver, timeout=5).until(EC.presence_of_element_located((By.CLASS_NAME, "ant-table-tbody")))
        children = parent.find_elements(By.TAG_NAME, "tr")
        children = children[1:-1]

        old_splits = grab_splits("splits.txt")

        with open("splits.txt", "w") as f:
            for child in children:
                grandchildren = child.find_elements(By.TAG_NAME, "td")

                for grandchild in grandchildren:
                    if len((grandchild.find_elements(By.TAG_NAME, "a"))) != 0 and grandchild.text != "Get Alert":
                        f.write(f"{grandchild.text}")
                    if ":" in grandchild.text:
                        f.write(f"@{grandchild.text}\n")

        driver.quit()

        new_splits = grab_splits("splits.txt")

        if new_splits == old_splits:
            pass
        else:
            keys = set(new_splits.keys()) - set(old_splits.keys())

            for key in keys:
                log.info(f"Stock: {key}\nRatio: {new_splits[key]}")
                post_to_webhook(ticker=key, ratio=new_splits[key])

        log.info("Going to sleep...zzz")
        time.sleep(DELAY_TIME)
        

if __name__ == "__main__":
    main()