# Class that inherits from a Selenium class. Given the direction of a land,
# it returns the postal code, the province and the locality

from selenium import webdriver
from selenium.webdriver.common.by import By
import logging
import time

import Correos.constants as const
import logger_config

logger = logging.getLogger(__name__)


class Correos(webdriver.Chrome):
    def __init__(self, delegation, lote, land, ref, direction):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        super().__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()
        self.delegation = delegation
        self.lote = lote
        self.land = land
        self.ref = ref
        self.direction = direction

    def get_data(self):
        try:
            self.__land_first_page()
            self.__close_cookies()
            self.__search()
            data = self.__get_info_about_search()
            cp, province, locality = data.values()

            # Log
            msg = f"Land '{self.ref}' is in '{province}' province. More precisely is on '{locality}' locality with C.P. {cp}"
            logger.info(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}"
            )
            return data
        except Exception:

            # Log
            msg = f"Failed to get 'cp, province, locality'."
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

    # Lands on a Correos webpage
    def __land_first_page(self):
        self.get(const.BASE_URL_CORREOS)

    def __close_cookies(self):
        reject_cookies_btn = self.find_element(
            By.XPATH, "//button[@aria-label='Rechazar todas las cookies']"
        )
        reject_cookies_btn.click()

    # Let the instance on the webpage that shows data about the direction
    def __search(self):
        try:
            self.__close_cookies()
        except Exception:
            pass
        search_input = self.find_element(
            By.XPATH,
            "//input[contains(@id, 'correos-ui-input') and @type='text']",
        )
        search_input.send_keys(self.direction)
        submit_btn = self.find_element(By.XPATH, "//button[@aria-label='BUSCAR']")
        submit_btn.click()

    # Scrape the webpage that shows info about direction.
    def __get_info_about_search(self):
        cp, province, locality = self.find_elements(
            By.XPATH,
            "//div[@slot='container-scroll']/div[contains(@class,'ui-list-result')][1]/following-sibling::div[1]//dd",
        )
        return {"cp": cp.text, "province": province.text, "locality": locality.text}
