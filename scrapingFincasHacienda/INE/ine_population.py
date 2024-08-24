# Class that inherits from a Selenium Class, given a "municipio" it extracts the population now, the population five years ago and the porcentual variation

import regex
import time
import logging
from unidecode import unidecode  # To remove acentos

# A través del catastro, voy a poder sacar el municipio
# A través de la web de correos, voy a poder sacar la localidad
from selenium import webdriver
from selenium.webdriver.common.by import By

import logger_config

logger = logging.getLogger(__name__)


class InePopulation(webdriver.Chrome):
    def __init__(self, delegation, lote, land, ref, place, locality):
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
        self.place = unidecode(place.lower())
        self.locality = locality

    def get_data(self):
        try:
            self.__land_first_page()
            self.__search_population()
            data = self.__get_population()

            # Log
            msg = f"Population info about land '{self.ref}' has been extracted successfully: Now -> {data['population_now']} /// Five years ago -> {data['population_before']}"
            logger.info(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}"
            )
            return data

        except Exception:

            # Log
            msg = f"Failed to get population data from land '{self.ref}' with locality '{self.locality}'"
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

    # Lands on an Ine webpage
    def __land_first_page(self):
        self.get("https://www.ine.es/nomen2/index.do")

    # Let the instance on the webpage that shows data about the ref
    def __search_population(self):
        location_input = self.find_element(By.XPATH, "//input[@id='nombrePoblacion']")
        location_input.send_keys(self.locality)

        submit_btn = self.find_element(
            By.XPATH, "//input[@id='nombrePoblacion']/following-sibling::input"
        )
        submit_btn.click()

    # Scrape the webpage that shows info about population.
    # Returns the population now and the population 5 years ago as well as the porcentual variation
    def __get_population(self):
        rows = self.find_elements(By.XPATH, "//tr[th[@class='lad']]")
        for row in rows:
            municipio_row = row.find_element(By.XPATH, "th[2]").text.split(" ", 1)[1]
            municipio_row_f = unidecode(municipio_row.lower())  # f stands for formatted
            if municipio_row_f in self.place:
                # The variable population_now will hold the population data from the last available year
                population_now = int(row.find_element(By.XPATH, "td[1]").text)
                # The variable population_before, will hold the population data from 5 years ago
                population_before = int(row.find_element(By.XPATH, "td[16]").text)
                porcentual_variation = (
                    population_now - population_before
                ) / population_before
                break
        return {
            "population_now": population_now,
            "population_before": population_before,
            "porcentual_variation": round(porcentual_variation, 2),
        }
