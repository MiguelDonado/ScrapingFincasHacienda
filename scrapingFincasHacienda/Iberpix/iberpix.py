import time
from pathlib import Path

import Iberpix.constants as const
from selenium import webdriver
from selenium.webdriver.common.by import By


class Iberpix(webdriver.Chrome):
    def __init__(self, delegation, lote, land, ref):
        options = webdriver.ChromeOptions()
        # Keep the browser open after the WebDriver session is terminated.
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-search-engine-choice-screen")
        # It supresses the logging messages that Chrome outputs to the console
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        #
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": str(const.DOWNLOAD_DIR),
                "download.prompt_for_download": False,  # Automatically save files to the specified directory without asking
                "download.directory_upgrade": True,  # Browser will not prompt the user when the download directory is changed
                "safebrowsing.enabled": True,  # Dunno the reason, maybe without it something pop-up alerting me or something
            },
        )
        super().__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()
        self.delegation = delegation
        self.lote = lote
        self.land = land
        self.ref = ref

    def get_data(self):
        self.__land_first_page()
        self.__search_land()

        # Curvas de nivel
        filename_mapa_curvas_nivel = f"{self.ref}{const.SUFFIX_FILENAME_CURVAS_NIVEL}"
        self.__my_get_screenshot(filename_mapa_curvas_nivel)

        # Lidar
        self.__show_lidar_map()
        filename_mapa_lidar = f"{self.ref}{const.SUFFIX_FILENAME_LIDAR}"
        self.__my_get_screenshot(filename_mapa_lidar)

        # Usos del suelo
        self.__show_usos_suelo_map()
        filename_mapa_usos_suelo = f"{self.ref}{const.SUFFIX_FILENAME_USOS_SUELO}"
        self.__my_get_screenshot(filename_mapa_usos_suelo)

    def __land_first_page(self):
        self.get(const.BASE_URL_IBERPIX)

    def __search_land(self):
        parcela_catastro_button = self.find_element(
            By.XPATH, "//div[@id='m-locator-infocatastro']"
        )
        parcela_catastro_button.click()

        catastro_button = self.find_element(
            By.XPATH, "//label[@id='tab-search-catastro']"
        )
        catastro_button.click()

        input_search_ref_catastral = self.find_element(
            By.XPATH, "//input[@id='m-refCatastral-input']"
        )
        input_search_ref_catastral.send_keys(self.ref)

        search_btn = self.find_element(
            By.XPATH, "//button[@id='m-infocatastro-refCatastral']"
        )
        search_btn.click()

        # To hide the pop-up, so we can see entirely the map
        parcela_catastro_button.click()

        # Close a popup that shows a bit the info about the land

        close_btn = self.find_element(
            By.XPATH,
            '//div[div[b[text()="Dirección exacta"]]]/preceding-sibling::div/a[@title="cerrar popup"]',
        )

        close_btn.click()

    def __show_lidar_map(self):
        choose_background_layer = self.find_element(
            By.XPATH, '//button[contains(@aria-label,"BackImgLayer")]'
        )
        choose_background_layer.click()

        lidar_btn = self.find_element(By.XPATH, '//img[@alt="LiDAR (Relieve)"]')
        lidar_btn.click()

        close_side_panel = self.find_element(
            By.XPATH, '//button[@aria-label="Plugin BackImgLayer"]'
        )
        close_side_panel.click()

    def __show_usos_suelo_map(self):
        choose_background_layer = self.find_element(
            By.XPATH, '//button[contains(@aria-label,"BackImgLayer")]'
        )
        choose_background_layer.click()

        usos_suelo_btn = self.find_element(
            By.XPATH, '//img[@alt="Ocupación del suelo (CORINE)"]'
        )
        usos_suelo_btn.click()

        close_side_panel = self.find_element(
            By.XPATH, '//button[@aria-label="Plugin BackImgLayer"]'
        )
        close_side_panel.click()

    def __my_get_screenshot(self, filename):
        # Build the filename that will have our downloader file
        path = const.DOWNLOAD_DIR / filename

        self.get_screenshot_as_file(path)

        return filename
