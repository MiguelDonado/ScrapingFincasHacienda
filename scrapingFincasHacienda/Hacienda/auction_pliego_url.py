# Functions used to extract the url of the Pliego PDF for a given auction url.

import requests
from bs4 import BeautifulSoup
from Hacienda.auction_get_data_pdf import read_pdf
import regex
import Hacienda.constants as const
import logging


def get_url_pliego_pdf(href, i_delegation):
    # Given the href of the auction, from all the anchor tags of the web page,
    # returns the href of the one that correspond to the Pliego PDF.
    html_text = requests.get(href)
    soup = BeautifulSoup(html_text.text, "lxml")
    pliego_pdf = soup.find("a", href=const.PLIEGO_PATTERN).get("href")
    url_pliego_pdf = const.BASE_URL_HACIENDA + pliego_pdf
    # If Pliego PDF, doesn't contain a list of lands in auction, check for Anexo PDF.
    if not has_ref_catastral(url_pliego_pdf):
        try:
            anexo_pdf = soup.find("a", href=const.ANEXO_PATTERN).get("href")
            url_pliego_pdf = const.BASE_URL_HACIENDA + anexo_pdf
            logging.info(
                f"{i_delegation} - X - X Lands'll be extracted from the anexo: {url_pliego_pdf}"
            )
        except Exception as e:
            logging.error(
                f"{i_delegation} - X - X Failed to find lands on PDF pliego or PDF anexo"
            )
            return None
    else:
        logging.info(
            f"{i_delegation} - X - X Lands'll be extracted from the pliego: {url_pliego_pdf}"
        )
    return url_pliego_pdf


def has_ref_catastral(url_pdf):
    # Sometimes the Pliego PDF doesn't contain the list of properties, but just the announcement,
    # and so the list of properties is detailed on another anchor tag
    text_pliego_pdf = read_pdf(url_pdf)
    has_ref_catastral_pliego = regex.search(
        const.REF_CATASTRAL_PATTERN, text_pliego_pdf
    )
    return has_ref_catastral_pliego
