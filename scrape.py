from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import time
import pandas as pd

class ScrapeLeaderboard:
    def __init__(self, driver_path: str, url: str):
        self.service = Service(executable_path=driver_path)
        self.url = url

    def get_leaders(self, driver: ChromeDriver) -> list[list[str]]:
        elements = driver.find_elements(By.CSS_SELECTOR, '.css-52oy3f')
        leaders = [[str(i)] + element.text.split('\n') for i, element in enumerate(elements, 1)]
        return leaders

    def get_rest(self, driver: ChromeDriver) -> list[list[str]]:
        elements = driver.find_elements(By.CSS_SELECTOR, '.css-1i8d91p')
        return [element.text.split('\n') for element in elements]

    def page_numb(self, driver: ChromeDriver) -> int:
        page_info_element = driver.find_element(By.CSS_SELECTOR, '.chakra-text.css-34iw3d')
        return int(page_info_element.text.split()[-1])

    def first_page(self, driver: ChromeDriver) -> list[list[str]]:
        leaders = self.get_leaders(driver)
        rest = self.get_rest(driver)
        return leaders + rest

    def other_pages(self, driver: ChromeDriver) -> list[list[str]]:
        next_page_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="season-leaderboard-next-page"]')
        next_page_button.click()
        time.sleep(5)
        return self.get_rest(driver)

    def scrape(self) -> list[list[str]]:
        driver = ChromeDriver(service=self.service)
        driver.get(self.url)
        time.sleep(5)
        pages = self.page_numb(driver)
        all_values = self.first_page(driver)
        for i in range(pages - 1):
            all_values += self.other_pages(driver)
        driver.quit()
        return all_values

    def scrape_to_df(self) -> pd.DataFrame:
        data = self.scrape()
        df = pd.DataFrame(data, columns=['Rank', 'ID', 'Value', 'Total'])
        df['Rank'] = df['Rank'].astype(int)
        df['Value'] = df['Value'].str.replace(',', '').astype(int)
        df['Total'] = df['Total'].str.replace('Total: ', '').str.replace(',', '').astype(int)
        df.to_csv('leaderboard.csv', index=False)  ## Save to csv as it takes a while to scrape
        return df