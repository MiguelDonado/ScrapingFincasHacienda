# Class that inherits from a Selenium Class, given a postal code, scrape some interesting data from the Sabi database website
import logging
import os
import sys
import time
from typing import Union

import logger_config
import pandas as pd
import Sabi.constants as const
from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

logger = logging.getLogger(__name__)

config = dotenv_values()


class Sabi(webdriver.Chrome):

    # Class attribute to store all instances
    all = []

    def __init__(self, delegation: int, lote: int, land: int, ref: str, cp: str):

        # Validate the data types of our arguments
        assert delegation > 0, f"Delegation {delegation} is not greater than zero!"
        assert lote > 0, f"Lote {lote} is not greater than zero!"
        assert land > 0, f"Land {land} is not greater than zero!"
        assert isinstance(ref, str), f"Ref {ref} must be a string!"
        assert isinstance(cp, (str, type(None))), f"C.P. {cp} must be a string or None!"

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
        self.cp = cp

        # Append new instance to the class attribute list
        Sabi.all.append(self)

    def __repr__(self):
        return f"Sabi({self.delegation}, {self.lote}, {self.land}, '{self.ref}', '{self.cp}')"

    def __str__(self):
        return (
            f"Sabi Object:\n"
            f"  Delegation: {self.delegation}\n"
            f"  Lote: {self.lote}\n"
            f"  Land: {self.land}\n"
            f"  Reference: {self.ref}\n"
            f"  C.P.: {self.cp}"
        )

    def get_data(self) -> pd.DataFrame:
        try:

            # Check if the data scraped from Correos work successfully or not
            # If not, then dont proceed any further with this class, log and return None
            if not self.cp:
                # Log
                msg = f"Scraping done with Correos class didn`t work succesfully for land '{self.ref}', the value of the argument data_correos['cp'] is {self.cp}, so the class {self.__class__.__name__} won't be used to scrape anything."
                logger.info(
                    f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}"
                )
                return None

            self.__land_first_page()
            self.__login()
            self.__filter_cp()
            self.__filter_status()
            self.__filter_last_year_available_financial_statements()
            data = self.__get_results()
            self.__logout()

            # Log
            msg = f"Enterprises near land '{self.ref}' located on C.P. {self.cp} have been extracted successfully: {data['Nombre'].tolist()}"
            logger.info(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}"
            )
            return data
        except Exception:

            # Log
            msg = f"Failed to extract enterprises near land '{self.ref}' located on C.P. {self.cp}."
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
    # Lands on Sabi UPC main webpage
    def __land_first_page(self) -> None:
        self.get(config["BASE_URL_SABI_UPC"])

    # Login in Sabi website
    def __login(self) -> None:
        input_name = self.find_element(By.XPATH, "//input[@id='edit-name']")
        input_name.send_keys(config["MY_UPC_ACCOUNT"])

        input_password = self.find_element(By.XPATH, "//input[@id='edit-pass']")
        input_password.send_keys(config["MY_UPC_PASSWORD"])

        submit_btn = self.find_element(By.XPATH, "//input[@id='submit_ok']")
        submit_btn.click()

    # On the main Sabi Menu (once login has been done) add the CP to the filters.
    def __filter_cp(self) -> None:
        alphabetical_list = self.find_element(
            By.XPATH, "//div[@class='alphabeticalIcon']/following-sibling::a"
        )
        alphabetical_list.click()

        cp_option = self.find_element(By.XPATH, "//a[text()='Código postal']")
        cp_option.click()

        # It ask us to introduce a range of postal codes, but we only wanna get info about one, so we put the same postal code on both
        min_cp_input = self.find_element(By.XPATH, "//input[contains(@id,'MinFree')]")
        min_cp_input.send_keys(self.cp)

        max_cp_input = self.find_element(By.XPATH, "//input[contains(@id,'MaxFree')]")
        max_cp_input.send_keys(self.cp)
        first_search_btn = self.find_element(
            By.XPATH, "//img[contains(@id, 'MultiMinMaxControl_SelectButton')]"
        )
        first_search_btn.click()

        accept_btn = self.find_element(
            By.XPATH, "//img[contains(@id, 'MultiMinMaxControl_Ok')]"
        )
        accept_btn.click()

    # On the main Sabi Menu (once login has been done) add the status to the filters.
    def __filter_status(self) -> None:
        status_button = self.find_element(By.XPATH, "//span[text()='Estatus']")
        status_button.click()

        # Select status 'Active'
        active_choice = self.find_element(
            By.XPATH,
            "//td[span[text() = 'Activa']]/preceding-sibling::td[1]//img[@style='cursor:hand;']",
        )
        active_choice.click()

        accept_btn = self.find_element(
            By.XPATH, "//img[@id='ContentContainer1_ctl00_Content_Ok']"
        )
        accept_btn.click()

    # On the main Sabi Menu (once login has been done) add the last year of available CCAA to the filters.
    def __filter_last_year_available_financial_statements(self) -> None:
        alphabetical_list = self.find_element(
            By.XPATH, "//div[@class='alphabeticalIcon']/following-sibling::a"
        )
        alphabetical_list.click()

        select_last_year_button = self.find_element(
            By.XPATH, "//a[text()='Año de las últimas cuentas']"
        )
        select_last_year_button.click()

        # For example if today is 24/06/2024:
        # choose_last_year_btn = 2023 and choose_penultimo_year_btn = 2022
        # And this would be dynamic for future years (because I'm selecting the [1] an [2] index)
        choose_last_year_btn = self.find_element(
            By.XPATH, "//table[contains(@id, 'SelectingList')]//tr[@data-lookuprid][1]"
        )

        choose_last_year_btn.click()
        choose_penultimo_year_btn = self.find_element(
            By.XPATH, "//table[contains(@id, 'SelectingList')]//tr[@data-lookuprid][2]"
        )
        choose_penultimo_year_btn.click()

        accept_btn = self.find_element(
            By.XPATH, "//img[@id='MasterContent_ctl00_Content_MultiChoiceControl_Ok']"
        )
        accept_btn.click()

    # On the main Sabi Menu (once login and filters has been done) get
    # the results (the first 25 results).
    # Returns a dataframe. It returns 61 colums because it's using the
    # default model that are using in Audicon to analyze the competence
    def __get_results(self) -> pd.DataFrame:
        watch_results = self.find_element(By.XPATH, "//img[contains(@id, 'GoToList')]")
        watch_results.click()
        self.__apply_competence_analysis_columns()

        headers = self.__get_results_cabeceras()
        names = self.__get_results_first_table()
        data = self.__get_results_second_table()

        df = self.__sabi_results_to_df(headers, names, data)
        return df

    def __apply_competence_analysis_columns(self) -> None:
        columns_button = self.find_element(
            By.XPATH,
            "//a[@id='ContentContainer1_ctl00_Content_ListHeader_ListHeaderRightButtons_AddRemoveColumns']",
        )
        columns_button.click()

        load_list_from_disk_btn = self.find_element(
            By.XPATH,
            "//img[@id='ContentContainer1_ctl00_Content_ListFormatsCollection_bnLoadFromDisk']",
        )
        load_list_from_disk_btn.click()

        file_input = self.find_element(
            By.XPATH,
            "//input[@id='ContentContainer1_ctl00_Content_ListFormatsCollection_LoadFromDisk_UploadedFile']",
        )
        file_input.send_keys(const.COLUMNAS_SABI)

        accept_btn = self.find_element(
            By.XPATH,
            "//img[@id='ContentContainer1_ctl00_Content_ListFormatsCollection_LoadFromDisk_OkButton']",
        )
        accept_btn.click()

        accept_btn = self.find_element(
            By.XPATH, "//img[@id='ContentContainer1_ctl00_Content_SaveFormat_OkButton']"
        )
        accept_btn.click()

    # On the results page, get the cabeceras of the table

    def __get_results_cabeceras(self) -> list[str]:
        row_cabeceras = self.find_element(
            By.XPATH,
            "//table[@id='ContentContainer1_ctl00_Content_ListCtrl1_LB1_VHDRTBL']/tbody/tr[last()]",
        )
        cabeceras = row_cabeceras.find_elements(By.XPATH, "./td[@id]")
        cabeceras = [
            self.__html_to_text(cabecera.get_attribute("innerHTML"))
            for cabecera in cabeceras
        ]
        cabeceras.insert(0, "Nombre")
        return cabeceras

    # On the results page, fetch the first table.
    # The first table contains only the names of the enterprises
    # The table covers the first 25 results, if we'd wanted to extract more,
    # we'd have to interact with another elements to move to the next pages.
    def __get_results_first_table(self) -> list[str]:
        table_first_25_elements_first_part = self.find_element(
            By.XPATH,
            "//table[@id='ContentContainer1_ctl00_Content_ListCtrl1_LB1_FDTBL']/tbody",
        )
        names_enterprises = table_first_25_elements_first_part.find_elements(
            By.XPATH,
            ".//a[@href='#']",
        )
        names_enterprises = [name.text for name in names_enterprises]
        return names_enterprises

    # This method fetches the second table from the results page
    # The second table contains all the data except the names
    # The table covers the first 25 results, if we'd wanted to extract more,
    # we'd have to interact with another elements to move to the next pages.
    def __get_results_second_table(self) -> list[list[Union[str, int]]]:
        data = []
        table_first_25_elements_second_part = self.find_element(
            By.XPATH,
            "//table[@id='ContentContainer1_ctl00_Content_ListCtrl1_LB1_VDTBL']/tbody",
        )
        rows = table_first_25_elements_second_part.find_elements(
            By.XPATH, "./tr[not(@id)]"
        )
        for row in rows:
            row_data = row.find_elements(
                By.XPATH, "./td[contains(@class, 'resultsItems')]"
            )
            row_data = [cell.text for cell in row_data]
            data.append(row_data)
        return data

    # Log out from Sabi website
    def __logout(self) -> None:
        logout_btn = self.find_element(By.XPATH, "//span[contains(@id,'logoutLabel')]")
        logout_btn.click()

        WebDriverWait(self, 30).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//span[@id='LoginTitleLabel']"), "DESCONEXIÓN"
            )
        )

    # We use static methods when we want to do something that is not unique per instance,
    # but it should do something that has a relationship with the class
    # I give this method three lists, and it returns me a dataframe.
    @staticmethod
    def __sabi_results_to_df(
        headers: list, names: list, data: list[list[Union[str, int]]]
    ) -> pd.DataFrame:
        # Combine names and data into a single list of rows
        combined_data = [[name] + row for name, row in zip(names, data)]

        # Create a dataframe
        df = pd.DataFrame(combined_data, columns=headers)
        return df

    @staticmethod
    def __html_to_text(html: str) -> str:
        return html.replace("<br>", " ").replace("\n", " ")
