# Functions used to extract the url of the Pliego PDF for a given auction.

import requests
from bs4 import BeautifulSoup
from scrapingFincasHacienda.Hacienda.hacienda_pliegopdf import read_pdf
import regex
import Hacienda.constants as const


def get_url_pliego_pdf(href):
    # Given the href of the auction, from all the anchor tags of the web page,
    # returns the href of the one that correspond to the Pliego PDF.
    html_text = requests.get(href)
    soup = BeautifulSoup(html_text.text, "lxml")
    pliego_pdf = soup.find("a", href=const.PLIEGO_PATTERN).get("href")
    url_pliego_pdf = const.BASE_URL_HACIENDA + pliego_pdf
    if check_has_ref_catastral(url_pliego_pdf):
        print(
            f"\no The following document will be used to extract the data: {url_pliego_pdf}"
        )
        return url_pliego_pdf
    else:
        anexo_pdf = soup.find("a", href=const.ANEXO_PATTERN).get("href")
        url_anexo_pdf = const.BASE_URL_HACIENDA + anexo_pdf
        print(
            f"\no The following document will be used to extract data: {url_anexo_pdf}"
        )
        return url_anexo_pdf


def check_has_ref_catastral(url_pdf):
    # Sometimes the Pliego PDF doesn't contain the list of properties, but just the announcement,
    # and so the list of properties is detailed on another anchor tag
    text_pliego_pdf = read_pdf(url_pdf)
    has_ref_catastral_pliego = regex.search(
        const.REF_CATASTRAL_PATTERN, text_pliego_pdf
    )
    return has_ref_catastral_pliego
