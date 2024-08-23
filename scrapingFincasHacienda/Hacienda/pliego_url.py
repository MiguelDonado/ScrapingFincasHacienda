# Functions used to extract the url of the Pliego/Anexo PDF for a given auction url.

import requests
import logging
from bs4 import BeautifulSoup
import regex

import logger_config
import Hacienda.constants as const
from Hacienda.data_pdf import read_pdf

# Logger configuration
logger = logging.getLogger(__name__)


def get_pliego(href, delegation):
    # Given the href of the auction, from all the anchor tags of the web page,
    # returns the href of the one that correspond to the Pliego PDF.
    html_text = requests.get(href)
    soup = BeautifulSoup(html_text.text, "lxml")
    pliego = soup.find("a", href=const.PLIEGO_PATTERN).get("href")
    url_pliego = const.BASE_URL_HACIENDA + pliego

    # If Pliego PDF doesn't contain a list of lands in auction, check for Anexo PDF.
    if not has_ref_catastral(url_pliego):
        try:
            anexo = soup.find("a", href=const.ANEXO_PATTERN).get("href")
            url_anexo = const.BASE_URL_HACIENDA + anexo

            # Log
            msg = f"List of lands: {url_anexo}"
            logger.info(f"{logger_config.build_id(delegation)}{msg}")

        except Exception:

            # Log
            msg = f"Failed to find list of lands on Pliego or Anexo."
            logger.error(f"{logger_config.build_id(delegation)}{msg}", exc_info=True)

            return None
    else:

        # Log
        msg = f"List of lands: {url_pliego}"
        logger.info(f"{logger_config.build_id(delegation)}{msg}")

    return url_pliego


def has_ref_catastral(url_pdf):
    # Sometimes the Pliego PDF doesn't contain the list of properties, but just the announcement,
    # and so the list of properties is detailed on another anchor tag
    text_pdf = read_pdf(url_pdf)
    return regex.search(const.REF_CATASTRAL_PATTERN, text_pdf)
