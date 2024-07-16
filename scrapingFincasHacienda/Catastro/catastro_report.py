# Class that uses Selenium to extract the reference value and downloads the price report PDF for a land

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import datetime
import os
import time
from dotenv import dotenv_values
import logging
import pdfplumber

config = dotenv_values()

# Get the current date
current_date = datetime.datetime.now()

# Format the date as dd/mm/yyyy
formatted_date = current_date.strftime("%d/%m/%Y")

# Directory where the PDF file would be saved
download_dir_pdf = "/home/miguel/coding-projects/ScrapingFincasHacienda/data/pdf/report"


class CatastroReport(webdriver.Chrome):
    def __init__(self, referencia_catastral, clase):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": download_dir_pdf,
                "download.propmt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
            },
        )
        super().__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()
        self.referencia_catastral = referencia_catastral
        self.clase = clase

    def land_first_page(self):
        self.get("https://www1.sedecatastro.gob.es/Accesos/SECAccvr.aspx")

    def close_cookies(self):
        accept_cookies = self.find_element(By.XPATH, "//a[@aria-label='allow cookies']")
        accept_cookies.click()

    def land_query_value_page(self):
        button_collapse = self.find_element(By.XPATH, "//a[@data-toggle='collapse']")
        button_collapse.click()
        query_value_button = self.find_element(
            By.XPATH, "//a[contains(text(),'Consulta de valor de referencia')]"
        )
        query_value_button.click()

    def access_with_dni(self):
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

    def select_date_and_property(self):
        ref_catastral_input = self.find_element(
            By.XPATH, "//input[@id='ctl00_Contenido_txtRC2']"
        )
        ref_catastral_input.send_keys(self.referencia_catastral)
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

    def get_reference_value_amount(self):
        value_label = self.find_element(
            By.XPATH,
            "//span[text()='Valor de Referencia']/following-sibling::div//label",
        )
        return self.format_price(value_label.text)

    # It'll retrieve the PDF report only if the land is "Rústico"
    # because on the rest of cases the PDF report is different and dont have
    # relevant data.
    # Cuando las fincas son rústicas proporciona a mayores un informe que contiene
    # datos relevantes, en el resto de casos (urbanas...) no tiene ese informe
    def get_reference_value_report(self):
        if self.clase == "Rústico":
            report_button = self.find_element(
                By.XPATH, "//input[@id='ctl00_Contenido_Button2']"
            )
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
            report_path = self.rename_pdf(self.referencia_catastral)
            return report_path
        else:
            return None

    # We use static methods when we want to do something that is not unique per instance,
    # but it should do something that has a relationship with the class
    @staticmethod
    def rename_pdf(ref_catastral):
        # Get the most recent file from the pdf destination directory
        most_recent_file = max(
            [os.path.join(download_dir_pdf, f) for f in os.listdir(download_dir_pdf)],
            key=os.path.getctime,
        )
        # Establish the variable that helds the new path
        new_file_path = os.path.join(download_dir_pdf, ref_catastral + ".pdf")
        os.rename(most_recent_file, new_file_path)
        return new_file_path

    @staticmethod
    def format_price(price):
        if not "€" in price:
            return None
        return float(
            price.replace("€", "").replace(" ", "").replace(".", "").replace(",", ".")
        )

    # Given the price report pdf for a land, it extract multiple data using pdfplumber library
    @staticmethod
    def process_report(report):
        # It'll return the text from the PDF file as one string
        with pdfplumber.open(file) as pdf:
            text_file = pdf.pages[0].extract_tables()
            ath, denominacion_ath, agrupacion_cultivo, one, agrupacion_municipio = (
                text_file[1][1]
            )
            two, three, four, number_buildings, slope, fls, *five = text_file[2][2]
            print(pdf.pages[0].extract_text())
        return {
            "ath": ath,
            "denominacion_ath": denominacion_ath,
            "agrupacion_cultivo": agrupacion_cultivo,
            "agrupacion_municipio": agrupacion_municipio,
            "number_buildings": number_buildings,
            "slope": slope,
            "fls": fls,
        }
