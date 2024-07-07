from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import datetime
import os
from dotenv import dotenv_values

config = dotenv_values()

# Get the current date
current_date = datetime.datetime.now()

# Format the date as dd/mm/yyyy
formatted_date = current_date.strftime("%d/%m/%Y")


class CatastroValue(webdriver.Chrome):
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        super().__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()

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

    def select_date_and_property(self, ref_catastral):
        ref_catastral_input = self.find_element(
            By.XPATH, "//input[@id='ctl00_Contenido_txtRC2']"
        )
        ref_catastral_input.send_keys(ref_catastral)
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
        return float(
            value_label.text.replace("€", "")
            .replace(" ", "")
            .replace(".", "")
            .replace(",", ".")
        )

    def get_reference_value_report(self):
        report_button = self.find_element(
            By.XPATH, "//input[@id='ctl00_Contenido_Button2']"
        )
        report_button.click()

        # Find iframe
        iframe = self.find_element(By.XPATH, "//iframe")

        # Switch to iframe
        self.switch_to.frame(iframe)

        download_pdf_button = self.find_element(
            By.XPATH, "//a[@id='ctl00_Contenido_ucPdf_LDescargaFichero']"
        )
        download_pdf_button.click()
