import requests
from bs4 import BeautifulSoup
from support_regex import ref_catastral_pattern
from pliegopdf import read_pdf
import regex


def get_url_pliego_pdf(href):
    html_text = requests.get(href)
    soup = BeautifulSoup(html_text.text, "lxml")
    anchors = soup.find_all("a")
    pliego_pdf = [
        anchor.get("href")
        for anchor in anchors
        if "liego" in anchor.get("href").lower()
    ]
    url_pliego_pdf = "https://www.hacienda.gob.es" + pliego_pdf[0]
    right_document = check_has_ref_catastral(url_pliego_pdf)
    if right_document:
        return url_pliego_pdf
    else:
        anexo_pdf = [
            anchor.get("href") for anchor in anchors if "nexo" in anchor.get("href")
        ]
        url_anexo_pdf = "https://www.hacienda.gob.es" + anexo_pdf[0]
        return url_anexo_pdf


def check_has_ref_catastral(url_pdf):
    text_pliego_pdf = read_pdf(url_pdf)
    has_ref_catastral_pliego = regex.search(ref_catastral_pattern, text_pliego_pdf)
    return has_ref_catastral_pliego
