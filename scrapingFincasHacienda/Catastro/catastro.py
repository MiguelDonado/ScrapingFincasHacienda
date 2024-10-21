# Class that inherits from a Selenium class. Given the referencia catastral of a property,
# it downloads the KML, and scrapes some data

import logging
import os
import time
from typing import Union

import Catastro.constants as const
import logger_config
import regex
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class Catastro(webdriver.Chrome):

    # Class attribute to store all instances
    all = []

    def __init__(
        self, delegation: int, lote: int, land: int, ref: str
    ):  # ref -> referencia catastral

        # Validate the data types of our arguments
        assert delegation > 0, f"Delegation {delegation} is not greater than zero!"
        assert lote > 0, f"Lote {lote} is not greater than zero!"
        assert land > 0, f"Land {land} is not greater than zero!"
        assert isinstance(ref, str), f"Ref {ref} must be a string!"

        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-search-engine-choice-screen")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": str(const.DOWNLOAD_DIR),
                "download.prompt_for_download": False,  # To automatically save files to the specified directory without asking
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
            },
        )
        super().__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()
        self.delegation = delegation
        self.lote = lote
        self.land = land
        self.ref = ref

        # Append new instance to the class attribute list
        Catastro.all.append(self)

    def __repr__(self):
        return f"Catastro({self.delegation}, {self.lote}, {self.land}, '{self.ref}')"

    def __str__(self):
        return (
            f"Catastro Object:\n"
            f"  Delegation: {self.delegation}\n"
            f"  Lote: {self.lote}\n"
            f"  Land: {self.land}\n"
            f"  Ref: {self.ref}"
        )

    # Returns a dictionary with 2 keys
    #    1) Data (again, a dictionary with 4 keys)
    #       1.1) localizacion
    #       1.2) clase
    #       1.3) uso
    #       1.4) cultivo_aprovechamiento
    #    2) Coordinates
    def get_data(self) -> dict[str, Union[dict[str, dict[str, str]], str]]:
        try:
            self.__land_first_page()
            self.__search()
            data = self.__scrape()
            path_ortofoto = self.__download_ortofoto()
            path_kml = self.__download_kml()
            coordinates = self.__get_coordenates_google_maps()
            # Log
            msg = f"Successfully downloaded PDF and KML of the land '{self.ref}' with coordinates '{coordinates}' and data: {data}."
            logger.info(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}"
            )
            return {
                "data": data,
                "coordinates": coordinates,
                "ortofoto": path_ortofoto,
                "kml": path_kml,
            }

        except Exception:

            # Log
            msg = f"Failed to get data from land '{self.ref}'"
            logger.error(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}",
                exc_info=True,
            )
        finally:
            self.quit()
            time.sleep(1)

    #
    #
    #
    #
    #
    #
    #
    ################################### PRIVATE METHODS ############################################
    #
    #
    #
    #
    #
    #
    #

    # Lands on the main Catastro webpage
    def __land_first_page(self) -> None:
        self.get(const.BASE_URL_SEARCH_CATASTRO)

    # Let the instance on the webpage that shows data about the ref.
    def __search(self) -> None:
        self.__close_cookies()
        input_search = self.find_element(
            By.XPATH, "//input[@id='ctl00_Contenido_txtRC2']"
        )
        input_search.send_keys(self.ref)
        button_submit = self.find_element(By.XPATH, "//input[@value='DATOS']")
        button_submit.click()

        # After clicking and navigating to a new page
        self.switch_to.default_content()  # Switch back to the main document context

    # Given the webpage that shows data about the ref, it scrapes some info
    # It returns a dictionary with four keys.
    def __scrape(self) -> dict[str, str]:
        localizacion = self.find_element(
            By.XPATH,
            "//div[@id='ctl00_Contenido_tblInmueble']//span[text()='Localización']/following-sibling::div//label",
        ).text
        provincia = regex.search(r".*\((.*)\)", localizacion).group(1)
        municipio = regex.search(
            r".*\. (.+)\(", localizacion, flags=regex.DOTALL
        ).group(1)
        clase = self.find_element(
            By.XPATH,
            "//div[@id='ctl00_Contenido_tblInmueble']//span[text()='Clase']/following-sibling::*//label",
        ).text
        uso = self.find_element(
            By.XPATH,
            "//div[@id='ctl00_Contenido_tblInmueble']//span[text()='Uso principal']/following-sibling::*//label",
        ).text
        if clase == "Rústico":
            cultivo = self.find_element(
                By.XPATH,
                "//table[@id='ctl00_Contenido_tblCultivos']//tr[2]//td[2]/span",
            ).text
        else:
            cultivo = None
        return {
            "localizacion": localizacion,
            "provincia": provincia,
            "municipio": municipio,
            "clase": clase,
            "uso": uso,
            "cultivo": cultivo,
        }

    # Given the webpage that shows data about the ref, it downloads the ortofoto of the land
    # and it goes back to the provided webpage
    def __download_ortofoto(self) -> None:
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
        path = self.__rename_file(self.ref, ".pdf")

        # Go back to the previous page
        self.back()

        return path

    # Given the webpage that shows data about the ref, it downloads the kml of the land
    # and it goes back to the provided webpage
    def __download_kml(self) -> None:
        self.__go_to_otros_visores()
        self.__change_to_new_window_tab()
        google_earth_kml = self.find_element(
            By.XPATH, "//img[@id='ctl00_Contenido_btnGoogleEarth']"
        )
        google_earth_kml.click()
        # Give time to the KML to be downloaded, before trying
        # to rename it, or do something with the file
        time.sleep(5)
        path = self.__rename_file(self.ref, ".kml")

        # Close focused window
        self.__close_current_window()

        # Change focus to the remaining window
        self.switch_to.window(self.window_handles[0])

        return path

    # Get coordinates from the land, to pass them as an argument
    # to the constructor when creating a GoogleMaps object
    def __get_coordenates_google_maps(self) -> str:
        self.__go_to_otros_visores()
        self.__change_to_new_window_tab()

        # A window handle is a unique identifier for a browser window or tab
        # Example of a window handle
        # window_handle = "CDwindow-1234ABCD5678EFGH9012IJKL"

        google_maps_input = self.find_element(
            By.XPATH, "//input[@id='ctl00_Contenido_ImgBGoogleMaps']"
        )
        google_maps_input.click()

        self.__change_to_new_window_tab(current_windows=2)
        self.__close_cookies_google()

        coordinates_element = self.find_element(
            By.XPATH, "//input[contains(@class, 'searchboxinput')]"
        )
        return coordinates_element.get_attribute("value")

    # It closes the actual window, and changes focus to the remaining one
    def __close_current_window(self) -> None:
        # Close the current window
        self.close()

        # Get the list of all open windows
        all_windows = self.window_handles

        # Switch to the only remaining window
        if len(all_windows) == 1:
            self.switch_to.window(all_windows[0])

    # Given the webpage that shows data about the ref, it goes to a webpage that have multiple visores.
    # Used by another methods.
    # Constitutes the building blocks for a lot of other methods.
    def __go_to_otros_visores(self) -> None:
        cartografia_collapse = self.find_element(
            By.XPATH, "//a[span[@id='ctl00_Contenido_lblCartografia']]"
        )
        cartografia_collapse.click()
        otros_visores_anchor = self.find_element(
            By.XPATH, "//a[@id='BMostrarCartoInternet']"
        )
        otros_visores_anchor.click()

    # Called indirectly by another method
    def __close_cookies(self) -> None:
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
    def __close_cookies_google(self) -> None:
        cookies_btn = self.find_element(
            By.XPATH, "//button[@aria-label='Aceptar todo']"
        )
        cookies_btn.click()

    # First, waits till a new window tab is opened.
    # Second, changes to the new window.
    # current_windows = 'Windows already opened not including the new window'
    def __change_to_new_window_tab(self, current_windows: int = 1) -> None:
        # Wait for a new window or tab
        WebDriverWait(self, 10).until(lambda d: len(d.window_handles) > current_windows)

        # Switch to the new window
        if len(self.window_handles) > current_windows:
            new_window_handle = self.window_handles[-1]
            self.switch_to.window(new_window_handle)

    # We use static methods when we want to do something that is not unique per instance,
    # but it should do something that has a relationship with the class

    # Change the name of the most recent file that is on the destination directory
    # And puts as the name the ref_catastral.
    @staticmethod
    def __rename_file(ref: str, ext: str) -> None:

        # Validate the data types of our arguments
        assert isinstance(ref, str), f"Ref {ref} must be a string!"
        assert isinstance(ext, str), f"Ext {ext} must be a string!"

        # Get the most recent file from the destination directory
        most_recent_file = max(
            [
                os.path.join(const.DOWNLOAD_DIR, f)
                for f in os.listdir(const.DOWNLOAD_DIR)
            ],
            key=os.path.getctime,
        )

        # Establish the variable that helds the new path
        new_file_path = os.path.join(const.DOWNLOAD_DIR, ref + ext)
        os.rename(most_recent_file, new_file_path)
        return new_file_path
