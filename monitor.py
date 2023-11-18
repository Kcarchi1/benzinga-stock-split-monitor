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

WEBHOOK_URL = "https://discord.com/api/webhooks/1175247382536003715/kalSxyq4iNm58w566UkcjGLv3J2x2BaovHpY_-A9ctd6JmEGND1jJ-Jn9WonCyMM9UZc"

WEBHOOK_DELAY = 2

OPTIONS = webdriver.ChromeOptions()
OPTIONS.add_argument("--disable-notifications")
OPTIONS.add_argument("--disable-blink-features=AutomationControlled")
OPTIONS.add_experimental_option("excludeSwitches", ["enable-automation"]) 
OPTIONS.add_experimental_option("useAutomationExtension", False) 


def grab_splits(filename: str) -> Union[dict[str, list[str]], None]:
    try:
        splits = {}
        with open(filename, "r") as f:
            lines = f.readlines()
            for line in lines:
                values = line.strip().split("@")
                splits[values[2]] = values[0:2] + values[3:8]

            return splits
    except FileNotFoundError:
        open(filename, "w").close()
        return grab_splits(filename)


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


def post_to_webhook(
    name: str, 
    ticker: str, 
    ratio: str, 
    market: str, 
    ex_date: str, 
    announcement_date: str
) -> None:
    time.sleep(WEBHOOK_DELAY)
    requests.post(url=WEBHOOK_URL, json=format_webhook(name=name, ticker=ticker, ratio=ratio, market=market, ex_date=ex_date, announcement_date=announcement_date))


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
                grandchild_list = [grandchild.text for grandchild in grandchildren]
                f.write(f"{'@'.join(grandchild_list)}\n")

        driver.quit()

        new_splits = grab_splits("splits.txt")

        if new_splits == old_splits:
            pass
        else:
            keys = set(new_splits.keys()) - set(old_splits.keys())

            for key in keys:
                log.info(f"Stock: {key}\nRatio: {new_splits[key][3]}")
                post_to_webhook(name=new_splits[key][1], ticker=key, ratio=new_splits[key][3], market=new_splits[key][2], ex_date=new_splits[key][0], announcement_date=new_splits[key][4])

        log.info("Going to sleep...zzz")
        time.sleep(DELAY_TIME)
        

if __name__ == "__main__":
    main()