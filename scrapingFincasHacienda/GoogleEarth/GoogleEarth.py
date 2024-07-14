import GoogleEarth.constants as const
from selenium import webdriver
from selenium.webdriver.common.by import By


class GoogleEarth(webdriver.Chrome):
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        super().__init__(options=options)
        self.maximize_window()
        self.implicitly_wait(15)

    def land_first_page(self):
        self.get(const.BASE_URL)
