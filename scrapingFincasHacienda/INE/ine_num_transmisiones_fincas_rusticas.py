# Class that extract the number of rural lands trades that's been on a province now, years before and get the porcentual variation
# The INE only provides this data for rural lands

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import logging
import time

import logger_config

logger = logging.getLogger(__name__)


class IneNumTransmisionesFincasRusticas(webdriver.Chrome):
    def __init__(self, delegation, lote, land, ref, cp: str):

        assert isinstance(cp, str), "cp must be a string"

        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        super().__init__(options=options)
        self.maximize_window()
        self.implicitly_wait(15)
        self.delegation = delegation
        self.lote = lote
        self.land = land
        self.ref = ref
        self.cp_two_digits_province = str(cp)[0:2]

    def get_data(self):
        try:
            self.__land_first_page()
            self.__close_cookies()
            self.__choose_province()
            self.__choose_transaction_type()
            self.__choose_past_year()
            self.__see_results()
            data = self.__get_results()

            # Log
            msg = f"Number of transactions of 'Fincas Rusticas' where land '{self.ref}' is located: Now -> {data['transactions_now']} /// Seven years ago -> {data['transactions_before']}"
            logger.info(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}"
            )
            return data

        except Exception:

            # Log
            msg = f"Failed to get number of transactions of the province where the land '{self.ref}' is located."
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
        self.get("https://www.ine.es/jaxiT3/Tabla.htm?t=6152")

    def __close_cookies(self):
        accept_btn = self.find_element(By.XPATH, "//a[@id='aceptarCookie']")
        accept_btn.click()

    # Deselect all the provinces, and select the right one
    def __choose_province(self):
        choose_province_selection = self.find_element(
            By.XPATH, "//select[@id='cri55176']"
        )
        select = Select(choose_province_selection)
        province_name_option = self.find_element(
            By.XPATH,
            f"//option[@class='jP_2' and contains(text(), '{self.cp_two_digits_province}')]",
        )
        province_visible_text = province_name_option.text
        select.deselect_all()
        select.select_by_visible_text(province_visible_text)

    # Deselect the default transaction type, and choose the right one
    def __choose_transaction_type(self):
        choose_tipo_transaccion = self.find_element(
            By.XPATH, "//select[@id='cri55177']"
        )
        select = Select(choose_tipo_transaccion)
        select.deselect_by_index(0)
        select.select_by_visible_text("Compraventa")

    # Select 7 years ago (the actual year is already selected)
    def __choose_past_year(self):
        choose_year_select = self.find_element(By.XPATH, "//select[@id='periodo']")
        select = Select(choose_year_select)
        select.select_by_index(7)

    # Let the instance on the results webpage
    def __see_results(self):
        see_results = self.find_element(By.XPATH, "//input[@id='botonConsulSele']")
        see_results.click()

    # Return a dictionary that contains 3 keys
    #   1) transactions_now
    #   2) transactions_before
    #   3) variation
    def __get_results(self):
        actual_year = int(
            self.find_element(
                By.XPATH, "//table[@id='tablaDatos']/tbody/tr/*[2]"
            ).text.replace(".", "")
        )

        seven_years_ago = int(
            self.find_element(
                By.XPATH, "//table[@id='tablaDatos']/tbody/tr/*[3]"
            ).text.replace(".", "")
        )

        variation = round((actual_year - seven_years_ago) / seven_years_ago, 2)
        return {
            "transactions_now": actual_year,
            "transactions_before": seven_years_ago,
            "variation": variation,
        }
