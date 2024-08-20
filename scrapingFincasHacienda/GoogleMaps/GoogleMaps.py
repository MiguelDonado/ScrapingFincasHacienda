# Class that inherits from a Selenium Class. It can be used in two ways
# 1) Given two directions calculates the distance and time that takes from one point to the other
# 2) Given a direction, we can take a screenshot of the place. We've to use the search_to method.


# I had two options to deal with Google Maps:
#   1. Through Google Maps API, particularly the Distance Matrix API to measure the distance between two points.
#   Using the API involves a cost (pay per usage fee)
#   2. Using Selenium to automate web browsing.
#   THis options doesn't have any cost.
# I choose Selenium because it's free and because it allows me to practice
# with Selenium library, XPATH, and Chrome Developer Tools.

import GoogleMaps.constants as const
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys


class GoogleMaps(webdriver.Chrome):
    def __init__(self, ref_catastral, to, from_=None):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        super().__init__(options=options)
        self.maximize_window()
        self.implicitly_wait(15)
        self.from_ = from_
        self.to = to
        self.referencia_catastral = ref_catastral

    def land_first_page(self):
        self.get(const.BASE_URL)

    def close_cookies(self):
        cookies_btn = self.find_element(
            By.XPATH, "//button[@aria-label='Aceptar todo']"
        )
        cookies_btn.click()

    def search_to(self):
        to_input = self.find_element(
            By.XPATH, "//input[contains(@class,'searchboxinput')]"
        )
        to_input.clear()
        to_input.send_keys(self.to)

        search_btn = self.find_element(
            By.XPATH, "//button[@id='searchbox-searchbutton']"
        )
        search_btn.click()

        how_to_get_btn = self.find_element(
            By.XPATH, "//button[@data-value='Cómo llegar']"
        )
        how_to_get_btn.click()

    def search_from_(self):
        from__input = self.find_element(
            By.XPATH, "//input[contains(@aria-label,'unto de partida')]"
        )
        from__input.clear()
        from__input.send_keys(self.from_)

        search_btn = self.find_element(By.XPATH, "//button[@aria-label='Buscar']")
        search_btn.click()

    def search(self):
        self.search_to()
        self.search_from_()

    def get_distance_time_on_car(self):
        on_car_btn = self.find_element(
            By.XPATH, "//button[.//img[@aria-label='En coche']]"
        )
        on_car_btn.click()

        WebDriverWait(self, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Copiar enlace']"))
        )
        time_label = self.find_element(
            By.XPATH,
            "//span[contains(@id, 'section-directions-trip')]/following-sibling::div//div[contains(text(), 'min')]",
        )
        distance_label = self.find_element(
            By.XPATH,
            "//span[contains(@id, 'section-directions-trip')]/following-sibling::div//div[contains(text(), 'km')]",
        )
        return {"time_on_car": time_label.text, "distance_on_car": distance_label.text}

    def get_distance_time_on_foot(self):
        on_foot_btn = self.find_element(By.XPATH, "//img[@aria-label='A pie']")
        on_foot_btn.click()

        WebDriverWait(self, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Copiar enlace']"))
        )
        time_label = self.find_element(
            By.XPATH,
            "//span[contains(@id, 'section-directions-trip')]/following-sibling::div//div[contains(text(), 'min')]",
        )
        distance_label = self.find_element(
            By.XPATH,
            "//span[contains(@id, 'section-directions-trip')]/following-sibling::div//div[contains(text(), 'km')]",
        )
        return {
            "time_on_foot": time_label.text,
            "distance_on_foot": distance_label.text,
        }

    # This method will be called only once per land
    # It'll take a screenshot about the land and the nearby interest points
    def get_screenshot(self):
        hide_panel_btn = self.find_element(
            By.XPATH,
            "//button[@aria-label='Ocultar el panel lateral' and contains(@jsaction, 'drawer.close')]",
        )
        hide_panel_btn.click()

        WebDriverWait(self, 30).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[@id='minimap']//button[contains(@aria-labelledby, 'overlay')]",
                )
            )
        ).click()
        zoom_out_button = self.find_element(By.XPATH, "//button[@id='widget-zoom-out']")
        zoom_out_button.click()
        screenshot_path = f"/home/miguel/coding-projects/ScrapingFincasHacienda/data/googlemaps/{self.referencia_catastral}.png"
        time.sleep(2)
        self.get_screenshot_as_file(screenshot_path)
