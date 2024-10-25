import time
from pathlib import Path

import Iberpix.constants as const
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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

        # 'Data_usos_suelo' is a dictionary
        data_usos_suelo = self.__scrape_usos_suelo_info()

        # Get ortofoto provisional with hidrografia
        self.__get_ortofoto()

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

        map_element = self.find_element(By.XPATH, "//canvas")

        actions = ActionChains(self)

        # Move the mouse to the middle of the map element (where the interested land is located)
        actions.move_to_element(map_element).click().perform()

        # The info about the current layers, takes a bit to load.
        # If I try to enter before loading, it kicks me out
        time.sleep(2)

        info_section = self.find_element(
            By.XPATH, "//div[contains(@class, 'm-has-tabs')]/div/div[@data-index=1]"
        )
        info_section.click()

        expand_data_land_usos_suelo = self.find_element(
            By.XPATH, '//div[p[strong[contains(text(), "CORINE")]]]'
        )
        expand_data_land_usos_suelo.click()

        # Get table that contains the specific info for the land
        data_land_usos_suelo = self.find_element(
            By.XPATH, "//table[@class='featureInfo']/tbody"
        )

        # Extract headers
        headers = data_land_usos_suelo.find_elements(By.XPATH, "./tr[1]/th")
        headers = [header.text for header in headers]

        # Extract values
        values = data_land_usos_suelo.find_elements(By.XPATH, "./tr[2]/td")
        values = [value.text for value in values]

        # Create a dictionary containing the headers and the values
        final_data = dict(zip(headers, values))

        # Close popup
        close_btn = self.find_element(By.XPATH, "//a[@title='cerrar popup']")
        close_btn.click()

        # Exit info mode
        info_mode_btn.click()

        return final_data

    def __get_ortofoto(self):
        self.__set_bg_empty_layer()
        # Hidrografia layer
        self.__add_layer(const.HIDROGRAFIA)
        # Ortofotos provisionales layer
        self.__add_layer(const.ORTOFOTOS_PROVISIONALES)

    def __set_bg_empty_layer(self):
        choose_background_layer = self.find_element(
            By.XPATH, '//button[contains(@aria-label,"BackImgLayer")]'
        )
        choose_background_layer.click()

        select_empty_layer = self.find_element(
            By.XPATH, "//div[@id='m-backimglayer-lyr-empty']"
        )
        select_empty_layer.click()

        close_side_panel = self.find_element(
            By.XPATH, '//button[@aria-label="Plugin BackImgLayer"]'
        )
        close_side_panel.click()

    # Explanation of arguments:
    # all: If we want to see all the sublayers for the given url_service
    # If we dont want to see all the sublayers but only one, we should:
    #    1. Set the all argument to False
    #    2. Provide:
    #       a) The name of the sublayer we want to see
    #       b) Specify the number of the sublayer we want to see (the 1º, the 2º...)
    def __add_layer(
        self, url_service, all=True, name_sublayer="", number_position_sublayer=0
    ):
        expand_layer_collapse_btn = self.find_element(
            By.XPATH, "//div[@title='Gestor de capas']/button"
        )
        expand_layer_collapse_btn.click()

        add_layer_btn = self.find_element(
            By.XPATH, "//button[@id='m-layerswitcher-addlayers']"
        )
        add_layer_btn.click()

        input_search = self.find_element(
            By.XPATH, "//input[@id='m-layerswitcher-addservices-search-input']"
        )
        input_search.send_keys(url_service)

        search_btn = self.find_element(
            By.XPATH, "//button[@id='m-layerswitcher-addservices-search-btn']"
        )
        search_btn.click()

        if all:
            add_layer_btn = self.find_element(
                By.XPATH, "//button[@id='m-layerswitcher-addservices-selectall']"
            )
            add_layer_btn.click()
        else:
            pass

        accept_btn = self.find_element(
            By.XPATH,
            "//div[@id='m-layerswitcher-addservices-results']//button[contains(@class,'m-layerswitcher-addservices-add')]",
        )
        accept_btn.click()

        close_sidebar = self.find_element(
            By.XPATH, "//button[@aria-label='Plugin Layerswitcher']"
        )
        close_sidebar.click()

    def __my_get_screenshot(self, filename):
        # The background layers takes a bit of time to load. If i dont set any time, the screenshot
        # is wrong, and i see nothing
        time.sleep(1)

        # Build the filename that will have our downloader file
        path = const.DOWNLOAD_DIR / filename

        self.get_screenshot_as_file(path)

        return filename
