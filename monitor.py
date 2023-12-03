import logging
import time
import sys
from datetime import datetime
from typing import Union

import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

WEBHOOK_URL = None

WEBHOOK_DELAY = 2

MONITOR_DELAY = 600 

HEADLESS_MODE = False

OPTIONS = webdriver.ChromeOptions()
OPTIONS.add_argument("--disable-notifications")
OPTIONS.add_argument("--disable-blink-features=AutomationControlled")
OPTIONS.add_experimental_option("excludeSwitches", ["enable-automation"]) 
OPTIONS.add_experimental_option("useAutomationExtension", False) 

if HEADLESS_MODE:
    OPTIONS.add_argument("--headless=new")


def grab_splits(filename: str) -> dict[str, list[str]]:
    try:
        splits = {}
        with open(filename, "r") as f:
            lines = f.readlines()
            
            for line in lines:
                values = line.strip().split("@")
                splits[values[2]] = values[0:2] + values[3:8]  # Setting stock tickers as Keys

            return splits
    except FileNotFoundError:
        open(filename, "w").close()
        return grab_splits(filename)


def format_webhook( 
        name: str, ticker: str, ratio: str, 
        market: str, ex_date: str, announcement_date: str) -> dict[str, Union[None, list, str]]:
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
        name: str, ticker: str, ratio: str, 
        market: str, ex_date: str, announcement_date: str) -> None:
    time.sleep(WEBHOOK_DELAY)
    requests.post(
        url=WEBHOOK_URL, 
        json=format_webhook(
            name=name, ticker=ticker, ratio=ratio,  market=market, ex_date=ex_date, announcement_date=announcement_date))


def main():
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    
    while True:
        log.info("Running Benzinga Monitor...")

        driver = webdriver.Chrome(options=OPTIONS)
        actions = ActionChains(driver)
        driver.get("https://www.benzinga.com/calendars/stock-splits")

        try:
            parent = WebDriverWait(driver=driver, timeout=5).until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        except TimeoutException:
            log.exception("Table element not found.")
            sys.exit(1)

        actions.send_keys_to_element(parent, Keys.PAGE_DOWN).perform()  # Scrolls through table to render table elements
        children = parent.find_elements(By.TAG_NAME, "tr")

        old_splits = grab_splits("splits.txt")
        with open("splits.txt", "w") as f:
            for child in children:
                grandchildren = child.find_elements(By.TAG_NAME, "td")
                grandchildren = [grandchild.text for grandchild in grandchildren]
                f.write(f"{'@'.join(grandchildren)}\n")  # Adding '@' to serve as a delimiter 

        driver.quit()

        new_splits = grab_splits("splits.txt")
        if new_splits == old_splits:
            log.info("No changes detected")
        else:
            keys = set(new_splits.keys()) - set(old_splits.keys())

            for key in keys:
                log.info(f"Stock: {key}\nRatio: {new_splits[key][3]}")
                post_to_webhook(
                    name=new_splits[key][1], 
                    ticker=key, 
                    ratio=new_splits[key][3], 
                    market=new_splits[key][2], 
                    ex_date=new_splits[key][0], 
                    announcement_date=new_splits[key][4]
                )

        log.info("Going to sleep...zzz")
        time.sleep(MONITOR_DELAY)
        

if __name__ == "__main__":
    main()