# Class that inherits from a Selenium class. Given the catastro url for a property, it downloads the KML, and scrapes some data

from selenium import webdriver
import Catastro.constants as const
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

download_dir = "/home/miguel/coding-projects/ScrapingFincasHacienda/data/kml"


class Catastro(webdriver.Chrome):
    def __init__(self, referencia_catastral):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,  # To automatically save files to the specified directory without asking
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
            },
        )
        super().__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()
        self.referencia_catastral = referencia_catastral

    def land_first_page(self):
        self.get(const.BASE_URL_SEARCH_CATASTRO)

    def close_cookies(self):
        # This is an HTML <iframe> element.
        # It is used to embed another HTML document within the current one

        # Locate cookie button of the main page
        button_cookie = self.find_element(
            By.XPATH,
            "//a[@aria-label='allow cookies']",
        )
        button_cookie.click()

        # Locate the iframe by its src attribute
        iframe = self.find_element(By.XPATH, "//iframe[@src]")

        # Switch to the iframe
        self.switch_to.frame(iframe)

        # Now i can interact with elements inside the iframe
        button_cookie_iframe = self.find_element(
            By.XPATH,
            "//a[@aria-label='allow cookies']",
        )
        button_cookie_iframe.click()

    def search(self):
        self.close_cookies()
        input_search = self.find_element(
            By.XPATH, "//input[@id='ctl00_Contenido_txtRC2']"
        )
        input_search.send_keys(self.referencia_catastral)
        button_submit = self.find_element(By.XPATH, "//input[@value='DATOS']")
        button_submit.click()

        # After clicking and navigating to a new page
        self.switch_to.default_content()  # Switch back to the main document context

    def get_info_about_search(self):
        localizacion_label = self.find_element(
            By.XPATH,
            "//div[@id='ctl00_Contenido_tblInmueble']//span[text()='Localización']/following-sibling::div//label",
        )
        clase_label = self.find_element(
            By.XPATH,
            "//div[@id='ctl00_Contenido_tblInmueble']//span[text()='Clase']/following-sibling::*//label",
        )
        uso_label = self.find_element(
            By.XPATH,
            "//div[@id='ctl00_Contenido_tblInmueble']//span[text()='Uso principal']/following-sibling::*//label",
        )
        if clase_label.text == "Rústico":
            cultivo_aprovechamiento_label = self.find_element(
                By.XPATH,
                "//table[@id='ctl00_Contenido_tblCultivos']//tr[2]//td[2]/span",
            ).text
        else:
            cultivo_aprovechamiento_label = None
        return {
            "localizacion": localizacion_label.text,
            "clase": clase_label.text,
            "uso": uso_label.text,
            "cultivo_aprovechamiento": cultivo_aprovechamiento_label,
        }

    def go_to_otros_visores(self):
        cartografia_collapse = self.find_element(
            By.XPATH, "//a[span[@id='ctl00_Contenido_lblCartografia']]"
        )
        cartografia_collapse.click()
        otros_visores_anchor = self.find_element(
            By.XPATH, "//a[@id='BMostrarCartoInternet']"
        )
        otros_visores_anchor.click()

    def download_kml(self):
        # Wait for a new window or tab
        WebDriverWait(self, 10).until(lambda d: len(d.window_handles) > 1)
        # Switch to the new window
        if len(self.window_handles) > 1:
            new_window_handle = self.window_handles[-1]
            self.switch_to.window(new_window_handle)

        google_earth_kml = self.find_element(
            By.XPATH, "//img[@id='ctl00_Contenido_btnGoogleEarth']"
        )
        google_earth_kml.click()
        time.sleep(5)

    @staticmethod
    def rename_kml(ref_catastral):
        most_recent_file = max(
            [os.path.join(download_dir, f) for f in os.listdir(download_dir)],
            key=os.path.getctime,
        )
        new_file_path = os.path.join(download_dir, ref_catastral, ".kml")
        os.rename(most_recent_file, new_file_path)
