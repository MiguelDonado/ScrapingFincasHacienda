import time
from pathlib import Path

import Iberpix.constants as const
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


class Iberpix(webdriver.Chrome):
    def __init__(self, delegation, lote, land, ref, kml_path):
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
        self.kml_path = kml_path

    def get_data(self):
        self.__land_first_page()
        self.__hide_menu()

        self.__add_land_kml_layer()

        # Curvas de nivel
        filename_mapa_curvas_nivel = f"{self.ref}{const.SUFFIX_FILENAME_CURVAS_NIVEL}"
        self.__my_get_screenshot(filename_mapa_curvas_nivel)

        # # Lidar
        self.__show_lidar_map()
        filename_mapa_lidar = f"{self.ref}{const.SUFFIX_FILENAME_LIDAR}"
        self.__my_get_screenshot(filename_mapa_lidar)

        # Usos del suelo
        self.__show_usos_suelo_map()
        filename_mapa_usos_suelo = f"{self.ref}{const.SUFFIX_FILENAME_USOS_SUELO}"
        self.__my_get_screenshot(filename_mapa_usos_suelo)
        self.__scrape_usos_suelo_info()

    def __land_first_page(self):
        self.get(const.BASE_URL_IBERPIX)

    def __hide_menu(self):
        hide_btn = self.find_element(By.XPATH, "//div[@id='m-locator-ignsearch']")
        hide_btn.click()

    # It also center my land on the middle of the map
    def __add_land_kml_layer(self):
        expand_menu_layers_btn = self.find_element(
            By.XPATH, "//button[@aria-label='Plugin Layerswitcher']"
        )
        expand_menu_layers_btn.click()

        add_layers_btn = self.find_element(
            By.XPATH, "//button[@id='m-layerswitcher-addlayers']"
        )
        add_layers_btn.click()

        time.sleep(3)

        upload_file_input = self.find_element(
            By.XPATH, "//input[@id='m-layerswitcher-addservices-file-input']"
        )
        upload_file_input.send_keys(self.kml_path)

        hide_side_bar_btn = self.find_element(
            By.XPATH, "//button[@aria-label='Plugin Layerswitcher']"
        )
        hide_side_bar_btn.click()

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

    def __scrape_usos_suelo_info(self):
        # To have the mouse on info mode, so i can click on the land in the map and get extra information
        info_mode_btn = self.find_element(By.XPATH, "//button[@id='m-information-btn']")
        info_mode_btn.click()

        time.sleep(5)
        # Get the size of the map element
        map_element = self.find_element(By.XPATH, "//canvas")
        map_size = map_element.size
        map_width = map_size["width"]
        map_height = map_size["height"]

        # Calculate the center point of the map
        center_x = map_width / 2
        center_y = map_height / 2

        actions = ActionChains(self)

        # ITS NOT WORKING !!!!
        # actions.move_to_element_with_offset(map_element, center_x, center_y).click().perform()

    def __my_get_screenshot(self, filename):
        # The background layers takes a bit of time to load. If i dont set any time, the screenshot
        # is wrong, and i see nothing
        time.sleep(1)

        # Build the filename that will have our downloader file
        path = const.DOWNLOAD_DIR / filename

        self.get_screenshot_as_file(path)

        return filename
