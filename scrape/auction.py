import requests
from bs4 import BeautifulSoup
from processpdf.constants import ref_catastral_pattern
from processpdf.pliegopdf import read_pdf
import regex
from scrape.constants import *


def get_url_pliego_pdf(href):
    html_text = requests.get(href)
    soup = BeautifulSoup(html_text.text, "lxml")
    pliego_pdf = soup.find("a", href=pliego_pattern).get("href")
    url_pliego_pdf = "https://www.hacienda.gob.es" + pliego_pdf
    if check_has_ref_catastral(url_pliego_pdf):
        print(
            f"\no The following document will be used to extract the data: {url_pliego_pdf}"
        )
        return url_pliego_pdf
    else:
        anexo_pdf = soup.find("a", href=anexo_pattern).get("href")
        url_anexo_pdf = "https://www.hacienda.gob.es" + anexo_pdf
        print(
            f"\no The following document will be used to extract data: {url_anexo_pdf}"
        )
        return url_anexo_pdf


def check_has_ref_catastral(url_pdf):
    text_pliego_pdf = read_pdf(url_pdf)
    has_ref_catastral_pliego = regex.search(ref_catastral_pattern, text_pliego_pdf)
    return has_ref_catastral_pliego
