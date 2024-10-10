# Class that inherits from a Selenium Class, given a "municipio" it extracts the population now, the population five years ago

import regex
import time
import logging
from unidecode import unidecode  # To remove acentos

# A través del catastro, voy a poder sacar el municipio
# A través de la web de correos, voy a poder sacar la localidad
from selenium import webdriver
from selenium.webdriver.common.by import By
from typing import Union

import logger_config

logger = logging.getLogger(__name__)


class InePopulation(webdriver.Chrome):

    # Class attribute to store all instances
    all = []

    def __init__(
        self, delegation: int, lote: int, land: int, ref: str, place: str, locality: str
    ):

        # Validate the data types of our arguments
        assert delegation > 0, f"Delegation {delegation} is not greater than zero!"
        assert lote > 0, f"Lote {lote} is not greater than zero!"
        assert land > 0, f"Land {land} is not greater than zero!"
        assert isinstance(ref, str), f"Ref {ref} must be a string!"
        assert isinstance(place, str), f"Place {place} must be a string!"
        assert isinstance(locality, str), f"Locality {locality} must be a string!"

        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-search-engine-choice-screen")
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

        # Append new instance to the class attribute list
        InePopulation.all.append(self)

    def __repr__(self):
        return f"InePopulation({self.delegation}, {self.lote}, {self.land}, '{self.ref}', '{self.place}', '{self.locality}')"

    def __str__(self):
        return (
            f"InePopulation Object\n"
            f"  Delegation: {self.delegation}\n"
            f"  Lote: {self.lote}\n"
            f"  Land: {self.land}\n"
            f"  Ref: {self.ref}\n"
            f"  Place: {self.place}\n"
            f"  Locality: {self.locality}"
        )

    def get_data(self) -> dict[str, Union[int, float]]:
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
    def __land_first_page(self) -> None:
        self.get("https://www.ine.es/nomen2/index.do")

    # Let the instance on the webpage that shows data about the ref
    def __search_population(self) -> None:
        location_input = self.find_element(By.XPATH, "//input[@id='nombrePoblacion']")
        location_input.send_keys(self.locality)

        submit_btn = self.find_element(
            By.XPATH, "//input[@id='nombrePoblacion']/following-sibling::input"
        )
        submit_btn.click()

    # Scrape the webpage that shows info about population.
    # Returns the population now and the population 5 years ago
    def __get_population(self) -> dict[str, Union[int, float]]:
        rows = self.find_elements(By.XPATH, "//tr[th[@class='lad']]")

        # Initialize variables
        population_now = None
        population_before = None

        for row in rows:
            municipio_row = row.find_element(By.XPATH, "th[2]").text.split(" ", 1)[1]
            municipio_row_f = unidecode(municipio_row.lower())  # f stands for formatted
            if municipio_row_f in self.place:
                # The variable population_now will hold the population data from the last available year
                population_now = int(row.find_element(By.XPATH, "td[1]").text)
                # The variable population_before, will hold the population data from 5 years ago
                population_before = int(row.find_element(By.XPATH, "td[16]").text)
            break
        return {
            "population_now": population_now,
            "population_before": population_before,
        }
