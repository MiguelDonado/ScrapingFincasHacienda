# Class that inherits from a Selenium Class, given a postal code, scrape some interesting data from the Sabi database website

from selenium import webdriver
from selenium.webdriver.common.by import By
import os
from dotenv import dotenv_values
import pandas as pd

config = dotenv_values()


class Sabi(webdriver.Chrome):
    def __init__(self, postal_code):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        super().__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()
        self.postal_code = postal_code

    def land_first_page(self):
        self.get("https://login.bvdinfo.com/R1/SabiInforma")

    def login(self):
        user = self.find_element(By.XPATH, "//input[@id='user']")
        user.send_keys(config["MY_SABI_ACCOUNT"])
        password = self.find_element(By.XPATH, "//input[@id='pw']")
        password.send_keys(config["MY_SABI_PASSWORD"])
        submit_btn = self.find_element(By.XPATH, "//input[@id='bnLoginNeo']")
        submit_btn.click()

    def filter_cp(self):
        alphabetical_list = self.find_element(
            By.XPATH, "//div[@class='alphabeticalIcon']/following-sibling::a"
        )
        alphabetical_list.click()

        postal_code_option = self.find_element(By.XPATH, "//a[text()='Código postal']")
        postal_code_option.click()

        # It ask us to introduce a range of postal codes, but we only wanna get info about one, so we put the same postal code on both
        min_postal_code_input = self.find_element(
            By.XPATH, "//input[contains(@id,'MinFree')]"
        )
        min_postal_code_input.send_keys(self.postal_code)

        max_postal_code_input = self.find_element(
            By.XPATH, "//input[contains(@id,'MaxFree')]"
        )
        max_postal_code_input.send_keys(self.postal_code)
        first_search_btn = self.find_element(
            By.XPATH, "//img[contains(@id, 'MultiMinMaxControl_SelectButton')]"
        )
        first_search_btn.click()

        accept_btn = self.find_element(
            By.XPATH, "//img[contains(@id, 'MultiMinMaxControl_Ok')]"
        )
        accept_btn.click()

    def filter_status(self):
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

    def filter_last_year_available_financial_statements(self):
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

    def get_results(self):
        watch_results = self.find_element(By.XPATH, "//img[contains(@id, 'GoToList')]")
        watch_results.click()

        headers = self.get_results_cabeceras()
        names = self.get_results_first_table()
        data = self.get_results_second_table()

        df = self.sabi_results_to_df(headers, names, data)
        return df

    # Called indirectly by another methods
    # This method fetches the headers from the results page
    def get_results_cabeceras(self):
        row_cabeceras = self.find_element(
            By.XPATH,
            "//table[@id='ContentContainer1_ctl00_Content_ListCtrl1_LB1_VHDRTBL']/tbody/tr[last()]",
        )
        cabeceras = row_cabeceras.find_elements(By.XPATH, "./td[@id]")
        cabeceras = [
            self.html_to_text(cabecera.get_attribute("innerHTML"))
            for cabecera in cabeceras
        ]
        cabeceras.insert(0, "Nombre")
        return cabeceras

    # Called indirectly by another methods
    # This method fetches the first table from the results page
    # The first table contains only the names of the enterprises
    # The table covers the first 25 results, if we'd wanted to extract more,
    # we'd have to interact with another elements to move to the next pages.
    def get_results_first_table(self):
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

    # Called indirectly by another methods
    # This method fetches the second table from the results page
    # The second table contains all the data except the names
    # The table covers the first 25 results, if we'd wanted to extract more,
    # we'd have to interact with another elements to move to the next pages.
    def get_results_second_table(self):
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

    def logout(self):
        logout_btn = self.find_element(By.XPATH, "//span[contains(@id,'logoutLabel')]")
        logout_btn.click()

    # We use static methods when we want to do something that is not unique per instance,
    # but it should do something that has a relationship with the class
    # I give this method three lists, and it returns me a dataframe.
    @staticmethod
    def sabi_results_to_df(headers, names, data):
        # Combine names and data into a single list of rows
        combined_data = [[name] + row for name, row in zip(names, data)]

        # Create a dataframe
        df = pd.DataFrame(combined_data, columns=headers)
        return df

    @staticmethod
    def html_to_text(html):
        return html.replace("<br>", " ").replace("\n", " ")
