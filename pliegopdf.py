import requests
from bs4 import BeautifulSoup
import re
import pdfplumber
import io


def read_pdf(url_pdf):
    response = requests.get(url_pdf)
    pdf_content = response.content
    pdf_file = io.BytesIO(pdf_content)
    with pdfplumber.open(pdf_file) as pdf:
        text_pages = [page.extract_text() for page in pdf.pages]
    return text_pages[10]


print(
    read_pdf(
        "https://www.hacienda.gob.es/DGPatrimonio/Gesti%C3%B3n%20Patrimonial/subastas/DEH%20OURENSE/Pliego_Sub.30_abril_2024.pdf"
    )
)
