# Class that inherits from a Selenium class. Given the catastro url for a property,
# it downloads the KML, and scrapes some data

import Catastro.constants as const
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Directory where the KML file would be saved
download_dir = "/home/miguel/coding-projects/ScrapingFincasHacienda/data/catastro"


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

    def download_img(self):
        cartografia_collapse = self.find_element(
            By.XPATH, "//a[span[@id='ctl00_Contenido_lblCartografia']]"
        )
        cartografia_collapse.click()

        cartografia_catastral_btn = self.find_element(
            By.XPATH, "//a[span[@id='ctl00_Contenido_lblMostrarCarto']]"
        )
        cartografia_catastral_btn.click()

        capas_btn = self.find_element(By.XPATH, "//button[@id='btnCapasC']")
        capas_btn.click()

        ortofoto_checkbox = self.find_element(By.XPATH, "//input[@id='aPNOA']")
        ortofoto_checkbox.click()

        expand_box_download_img = self.find_element(
            By.XPATH, "//button[i[@id='IBImprimir']]"
        )
        expand_box_download_img.click()

        choose_scale_input = self.find_element(By.XPATH, "//input[@id='txtEscala']")
        choose_scale_input.clear()
        choose_scale_input.send_keys("4000")

        download_img = self.find_element(
            By.XPATH, "//input[@id='ctl00_Contenido_bImprimir']"
        )
        download_img.click()
        # Give time to the pdf to be downloaded, before trying
        # to rename it, or do something with the file
        time.sleep(5)
        self.rename_file(self.referencia_catastral, ".pdf")

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
        self.wait_for_a_new_window_tab()
        google_earth_kml = self.find_element(
            By.XPATH, "//img[@id='ctl00_Contenido_btnGoogleEarth']"
        )
        google_earth_kml.click()
        # Give time to the KML to be downloaded, before trying
        # to rename it, or do something with the file
        time.sleep(5)
        self.rename_file(self.referencia_catastral, ".kml")

    # Get coordinates from the land, to pass them as an argument
    # to the constructor when creating a GoogleMaps object
    def get_coordenates_google_maps(self):
        google_maps_input = self.find_element(
            By.XPATH, "//input[@id='ctl00_Contenido_ImgBGoogleMaps']"
        )
        google_maps_input.click()
        self.wait_for_a_new_window_tab()
        self.close_cookies_google()

        coordinates_element = self.find_element(
            By.XPATH, "//input[contains(@class, 'searchboxinput')]"
        )
        return coordinates_element.get_attribute("value")

        # Called indirectly by another method

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

    # Called indirectly by another method
    def close_cookies_google(self):
        cookies_btn = self.find_element(
            By.XPATH, "//button[@aria-label='Aceptar todo']"
        )
        cookies_btn.click()

    # Called indirectly by another methods
    def wait_for_a_new_window_tab(self):
        # Wait for a new window or tab
        WebDriverWait(self, 10).until(lambda d: len(d.window_handles) > 1)
        # Switch to the new window
        if len(self.window_handles) > 1:
            new_window_handle = self.window_handles[-1]
            self.switch_to.window(new_window_handle)

    # We use static methods when we want to do something that is not unique per instance,
    # but it should do something that has a relationship with the class
    @staticmethod
    def rename_file(ref_catastral, extension):
        # Get the most recent file from the kml destination directory
        most_recent_file = max(
            [os.path.join(download_dir, f) for f in os.listdir(download_dir)],
            key=os.path.getctime,
        )
        # Establish the variable that helds the new path
        new_file_path = os.path.join(download_dir, ref_catastral + extension)
        os.rename(most_recent_file, new_file_path)
