import logging
import time

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


def post_to_webhook(message: str) -> None:
    time.sleep(WEBHOOK_DELAY)
    requests.post(url=WEBHOOK_URL, json={"content": message})


def main():
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    log.info("Running Benzinga Monitor...")
    while True:
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
                message = f"Stock: {key}\nRatio: {new_splits[key]}"
                log.info(message)
                post_to_webhook(message=message)


        log.info("Going to sleep...zzz")
        time.sleep(DELAY_TIME)
        

if __name__ == "__main__":
    main()