from Sabi.sabi import Sabi
from bs4 import BeautifulSoup
import pandas as pd

item = Sabi("15894")
item.land_first_page()
item.login()
item.filter_cp()
item.filter_status()
item.filter_last_year_available_financial_statements()
item.get_results()
# item.logout()
