# Class that uses Selenium to extract the reference value
# and downloads the price report PDF for a land

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import datetime
import os
import time
from dotenv import dotenv_values
import pdfplumber

import logging
import logger_config
import Catastro.constants as const

logger = logging.getLogger(__name__)

config = dotenv_values()

# Get the current date
current_date = datetime.datetime.now()

# Format the date as dd/mm/yyyy
formatted_date = current_date.strftime("%d/%m/%Y")


class CatastroReport(webdriver.Chrome):
    def __init__(self, delegation, lote, land, referencia_catastral, clase):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": const.DOWNLOAD_DIR_REPORT,
                "download.propmt_for_download": False,
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
        self.ref = referencia_catastral
        self.clase = clase

    # Scrape the reference value and download the 'Report PDF' if the land is 'Rústico'
    def get_data(self):
        try:
            self.__land_first_page()
            self.__close_cookies()
            self.__access_query_value_page()
            self.__insert_dni()
            self.__select_date_and_property()
            reference_value = self.__get_reference_value()

            if self.clase == "Rústico":
                report = self.__get_reference_value_report()
                if report:
                    data_report = self.__process_report(report)
                else:
                    data_report = None
            else:  # No report PDF will be downloaded
                data_report = None

            # Log
            dynamic_msg = (
                f"The report PDF has been downloaded because it's 'Rústico'."
                if data_report
                else ""
            )
            msg = f"The land '{self.ref}' has the next value {reference_value}. {dynamic_msg}"
            logger.info(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}",
            )

            return {"value": reference_value, "data": data_report}
        except Exception:

            # Log
            msg = f"Failed to get the reference value and the 'Report PDF' of the land '{self.ref}'"
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
    ################################### PRIVATE METHODS ############################################
    #
    #
    #
    #
    #
    #
    #

    # Lands on the main Catastro Report webpage
    def __land_first_page(self):
        self.get("https://www1.sedecatastro.gob.es/Accesos/SECAccvr.aspx")

    def __close_cookies(self):
        accept_cookies = self.find_element(By.XPATH, "//a[@aria-label='allow cookies']")
        accept_cookies.click()

    # Navigate to the query value webpage
    def __access_query_value_page(self):
        button_collapse = self.find_element(By.XPATH, "//a[@data-toggle='collapse']")
        button_collapse.click()
        query_value_button = self.find_element(
            By.XPATH, "//a[contains(text(),'Consulta de valor de referencia')]"
        )
        query_value_button.click()

    # Given the query value webpage, introduce DNI on the form
    def __insert_dni(self):
        dni_input = self.find_element(By.XPATH, "//input[@id='ctl00_Contenido_nif']")
        dni_input.clear()
        dni_input.send_keys(config["MY_DNI"])
        num_soporte_input = self.find_element(
            By.XPATH, "//input[@id='ctl00_Contenido_soporte']"
        )
        num_soporte_input.clear()
        num_soporte_input.send_keys(config["MY_DNI_SUPPORT_NUM"])
        validate_button = self.find_element(
            By.XPATH, "//button[@id='ctl00_Contenido_bAceptar']"
        )
        validate_button.click()

    # Given the query value webpage, introduce date on the form
    def __select_date_and_property(self):
        ref_catastral_input = self.find_element(
            By.XPATH, "//input[@id='ctl00_Contenido_txtRC2']"
        )
        ref_catastral_input.send_keys(self.ref)
        date_input = self.find_element(
            By.XPATH, "//input[@id='ctl00_Contenido_txtFechaConsulta']"
        )
        date_input.send_keys(formatted_date)

        # Finding the select element
        purpose_input = self.find_element(
            By.XPATH, "//select[@id='ctl00_Contenido_ddlFinalidad']"
        )
        # Create a select objetc
        select = Select(purpose_input)
        select.select_by_value("1")

        submit_button = self.find_element(
            By.XPATH, "//input[@id='ctl00_Contenido_btnValorReferencia']"
        )
        submit_button.click()

    # Given the final webpage, scrape the reference value
    def __get_reference_value(self):
        value_label = self.find_element(
            By.XPATH,
            "//span[text()='Valor de Referencia']/following-sibling::div//label",
        )
        return self.__format_price(value_label.text)

    # Download and return the name of the PDF report only if the land is "Rústico" because
    # on the rest of cases the PDF report is different and dont have relevant data.
    def __get_reference_value_report(self):
        try:
            report_button = self.find_element(
                By.XPATH, "//input[@id='ctl00_Contenido_Button2']"
            )
        except Exception:

            # Log
            msg = f"The land '{self.ref}' is '{self.clase}' but doesn't has a report."
            logger.warning(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}"
            )
            return None

        # If there's no report for the land
        if not report_button:
            return None

        report_button.click()

        WebDriverWait(self, 30).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe"))
        )
        download_pdf_button = self.find_element(
            By.XPATH, "//a[@id='ctl00_Contenido_ucPdf_LDescargaFichero']"
        )
        download_pdf_button.click()
        # Give time to the PDF to be downloaded, before trying
        # to rename it, or do something with the file
        time.sleep(5)
        report_path = self.__rename_pdf(self.ref)
        return report_path

    # We use static methods when we want to do something that is not unique per instance,
    # but it should do something that has a relationship with the class
    @staticmethod
    def __rename_pdf(ref_catastral):
        # Get the most recent file from the pdf destination directory
        most_recent_file = max(
            [
                os.path.join(const.DOWNLOAD_DIR_REPORT, f)
                for f in os.listdir(const.DOWNLOAD_DIR_REPORT)
            ],
            key=os.path.getctime,
        )
        # Establish the variable that helds the new path
        new_file_path = os.path.join(const.DOWNLOAD_DIR_REPORT, ref_catastral + ".pdf")
        os.rename(most_recent_file, new_file_path)
        return new_file_path

    @staticmethod
    def __format_price(price):
        if not "€" in price:
            return None
        return float(
            price.replace("€", "").replace(" ", "").replace(".", "").replace(",", ".")
        )

    # Given the price report pdf, it extracts relevant data
    @staticmethod
    def __process_report(report):
        # It'll return the text from the PDF file as one string
        with pdfplumber.open(report) as pdf:
            text_file = pdf.pages[0].extract_tables()
            ath, denominacion_ath, agrupacion_cultivo, one, agrupacion_municipio = (
                text_file[1][1]
            )
            two, three, four, number_buildings, slope, fls, *five = text_file[2][2]
        return {
            "ath": ath,
            "denominacion_ath": denominacion_ath,
            "agrupacion_cultivo": agrupacion_cultivo,
            "agrupacion_municipio": agrupacion_municipio,
            "number_buildings": number_buildings,
            "slope": slope,
            "fls": fls,
        }
