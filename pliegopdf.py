import requests
from bs4 import BeautifulSoup
import re
import pdfplumber
import io
from support_regex import (
    paragraphs_pattern,
    rusticas_ref_catastral_pattern,
    urbanas_ref_catastral_pattern,
    price_pattern,
)


def get_pliego_relevant_info(url_pdf):
    text = read_pdf(url_pdf)
    paragraphs = get_desired_paragraphs(text)
    final_data = [get_desired_information(paragraph) for paragraph in paragraphs]
    return final_data


def read_pdf(url_pdf):
    response = requests.get(url_pdf)
    pdf_content = response.content
    pdf_file = io.BytesIO(pdf_content)
    with pdfplumber.open(pdf_file) as pdf:
        text_pages = [page.extract_text() for page in pdf.pages]
    all_text_file = " ".join(text_pages)
    return all_text_file


url = "https://www.hacienda.gob.es/DGPatrimonio/Gesti%C3%B3n%20Patrimonial/subastas/DEH%20OURENSE/Pliego_Sub.30_abril_2024.pdf"


def get_desired_paragraphs(all_text_pdf):
    return re.findall(paragraphs_pattern, all_text_pdf)


def get_desired_information(paragraph):
    return (get_ref_catastral(paragraph), get_precio(paragraph))


def get_ref_catastral(paragraph):
    ref_catastral = re.search(rusticas_ref_catastral_pattern, paragraph)
    if ref_catastral:
        return ref_catastral.group()
    else:
        ref_catastral = re.search(urbanas_ref_catastral_pattern, paragraph)
        return ref_catastral.group()


def get_precio(paragraph):
    price = re.search(price_pattern, paragraph)
    return format_price(price.group())


def format_price(price):
    return float(
        price.replace(".", "").replace(",", ".").replace(" ", "").replace("€", "")
    )
