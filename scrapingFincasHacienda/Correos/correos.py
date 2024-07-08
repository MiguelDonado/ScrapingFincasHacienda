# Class that inherits from a Selenium class. Given the direction of a land, it returns the postal code,
# the province and the locality

from selenium import webdriver
import Correos.constants as const
from selenium.webdriver.common.by import By


class Correos(webdriver.Chrome):
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        super().__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()

    def land_first_page(self):
        self.get(const.BASE_URL_CORREOS)

    def close_cookies(self):
        reject_cookies_btn = self.find_element(
            By.XPATH, "//button[@aria-label='Rechazar todas las cookies']"
        )
        reject_cookies_btn.click()

    def search(self, direction):
        self.close_cookies()
        search_input = self.find_element(
            By.XPATH,
            "//input[contains(@id, 'correos-ui-input') and @type='text']",
        )
        search_input.send_keys(direction)
        submit_btn = self.find_element(By.XPATH, "//button[@aria-label='BUSCAR']")
        submit_btn.click()

    def get_info_about_search(self):
        cp, province, locality = self.find_elements(
            By.XPATH,
            "//div[@slot='container-scroll']/div[contains(@class,'ui-list-result')][1]/following-sibling::div[1]//dd",
        )
        return cp, province, locality
