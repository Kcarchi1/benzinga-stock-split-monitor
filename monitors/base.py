from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from requests import Session


class Monitor(ABC):
    @abstractmethod
    def run(self):
        pass
    
    @abstractmethod
    def standardize(self, listings):
        pass


class BaseSeleniumMonitor(Monitor):
    def __init__(self, url):
        self.url = url
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--disable-notifications")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        self.options.add_experimental_option("useAutomationExtension", False)
        self.driver = webdriver.Chrome(options=self.options)

    def launch_site(self):
        self.driver.get(self.url)

    def close_site(self):
        self.driver.quit()

    def get_table_body_element(self):
        tbody = WebDriverWait(driver=self.driver, timeout=5).until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        return tbody

    def get_table_row_elements(self, body):
        return body.find_elements(By.TAG_NAME, "tr")
        
    def get_data_cell_elements(self, rows):
        data_cell_list = []
        for row in rows:
            data_cells = row.find_elements(By.TAG_NAME, "td")
            content = [data_cell.text for data_cell in data_cells]

            if len(content) <= 1:
                continue

            data_cell_list.append(self._to_dict(content))

        return data_cell_list
    
    def _to_dict(self, data_list):
        return dict(enumerate(data_list))


class BaseRequestsMonitor(Monitor):
    def __init__(self, url):
        self.url = url
        self.session = Session()
    
    