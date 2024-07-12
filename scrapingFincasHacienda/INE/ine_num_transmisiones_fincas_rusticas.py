# Class that extract the number of rural lands trades that's been on a province now, years before and get the porcentual variation
# The INE only provides this data for rural lands

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


class IneNumTransmisionesFincasRusticas(webdriver.Chrome):
    def __init__(self, cp_two_digits_province):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        super().__init__(options=options)
        self.maximize_window()
        self.implicitly_wait(15)
        self.cp_two_digits_province = cp_two_digits_province

    def land_first_page(self):
        self.get("https://www.ine.es/jaxiT3/Tabla.htm?t=6152")

    def close_cookies(self):
        accept_btn = self.find_element(By.XPATH, "//a[@id='aceptarCookie']")
        accept_btn.click()

    def choose_province(self):
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

    def choose_transaction_type(self):
        choose_tipo_transaccion = self.find_element(
            By.XPATH, "//select[@id='cri55177']"
        )
        select = Select(choose_tipo_transaccion)
        select.deselect_by_index(0)
        select.select_by_visible_text("Compraventa")

    def choose_year(self):
        choose_year_select = self.find_element(By.XPATH, "//select[@id='periodo']")
        select = Select(choose_year_select)
        select.select_by_index(7)

    def see_results(self):
        see_results = self.find_element(By.XPATH, "//input[@id='botonConsulSele']")
        see_results.click()

    def get_results(self):
        self.see_results()
        value_actual_year = int(
            self.find_element(
                By.XPATH, "//table[@id='tablaDatos']/tbody/tr/*[2]"
            ).text.replace(".", "")
        )

        value_seven_years_ago = int(
            self.find_element(
                By.XPATH, "//table[@id='tablaDatos']/tbody/tr/*[3]"
            ).text.replace(".", "")
        )

        variation = round(
            (value_actual_year - value_seven_years_ago) / value_seven_years_ago, 2
        )
        return {
            "transactions_now": value_actual_year,
            "transactions_before": value_seven_years_ago,
            "variation": variation,
        }
