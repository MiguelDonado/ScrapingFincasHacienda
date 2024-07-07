import regex


# A través del catastro, voy a poder sacar el municipio
# A través de la web de correos, voy a poder sacar la localidad
from selenium import webdriver
from selenium.webdriver.common.by import By


class Ine(webdriver.Chrome):
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        super().__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()

    def land_first_page(self):
        self.get("https://www.ine.es/nomen2/index.do")

    def get_population_now_before(self, municipio):
        rows = self.find_elements(By.XPATH, "//tr[th[@class='lad']]")
        for row in rows:
            municipio_row = row.find_element(By.XPATH, "th[2]").text.split(" ", 1)[1]
            if municipio_row.lower() == municipio.lower():
                population_now = int(row.find_element(By.XPATH, "td[1]").text)
                # Five years ago
                population_before = int(row.find_element(By.XPATH, "td[16]").text)
                porcentual_variation = (
                    population_now - population_before
                ) / population_before
                break
        return [population_now, population_before, porcentual_variation]

    def search_location_population(self, municipio, localidad):
        location_input = self.find_element(By.XPATH, "//input[@id='nombrePoblacion']")
        location_input.send_keys(localidad)

        submit_btn = self.find_element(
            By.XPATH, "//input[@id='nombrePoblacion']/following-sibling::input"
        )
        submit_btn.click()
        return self.get_population_now_before(municipio)
