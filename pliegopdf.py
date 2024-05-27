import requests
from bs4 import BeautifulSoup
import re
import pdfplumber
import io
from support_regex import (
    checker_second_structure_pattern,
    first_paragraphs_pattern,
    second_paragraphs_pattern,
    ref_catastral_pattern,
    price_first_structure_pdf_pattern,
    checker_garantia_in_paragraph_pattern,
    price_second_structure_pdf_with_garantia_pattern,
    price_second_structure_pdf_without_garantia_pattern,
    checker_second_structure_price_in_table_format,
    price_second_structure_pdf_with_garantia_pattern_and_table_format,
    checker_second_structure_price_not_in_the_paragraph,
    price_when_is_not_in_paragraph,
)


def get_pliego_relevant_info(url_pdf):
    text = read_pdf(url_pdf)
    paragraphs = get_desired_paragraphs(text)

    if paragraphs[0] == "first_structure":
        final_data = [
            get_desired_information("first", paragraph) for paragraph in paragraphs[1]
        ]
    elif paragraphs[0] == "second_structure":
        final_data = [
            get_desired_information("second", paragraph) for paragraph in paragraphs[1]
        ]
    # If the prices are not included on the same paragraph, but all together at the end.
    if final_data[0][1] == "0":
        prices = re.findall(price_when_is_not_in_paragraph, text)
        ref_catastrales = [item[0] for item in final_data]
        final_data = zip(ref_catastrales, prices)
    return final_data


def read_pdf(url_pdf):
    response = requests.get(url_pdf)
    pdf_content = response.content
    pdf_file = io.BytesIO(pdf_content)
    with pdfplumber.open(pdf_file) as pdf:
        text_pages = [page.extract_text() for page in pdf.pages]
    all_text_file = " ".join(text_pages[0:6])
    return all_text_file


url = "https://www.hacienda.gob.es/DGPatrimonio/Gesti%C3%B3n%20Patrimonial/subastas/DEH%20OURENSE/Pliego_Sub.30_abril_2024.pdf"


def get_desired_paragraphs(all_text_pdf):
    if re.search(checker_second_structure_pattern, all_text_pdf):
        return "second_structure", re.findall(second_paragraphs_pattern, all_text_pdf)
    else:
        return "first_structure", re.findall(first_paragraphs_pattern, all_text_pdf)


def get_desired_information(type_structure, paragraph):
    try:
        return (get_ref_catastral(paragraph), get_precio(type_structure, paragraph))
    except AttributeError:
        return ("ERROR", "ERROR")


def get_ref_catastral(paragraph):
    ref_catastrales = re.findall(ref_catastral_pattern, paragraph)
    if len(ref_catastrales) == 1:
        return ref_catastrales
    elif len(ref_catastrales) > 1:
        return ref_catastrales
    else:
        raise AttributeError("There is not a valid referencia catastral")


def get_precio(type_structure, paragraph):
    if type_structure == "first":
        price = re.search(price_first_structure_pdf_pattern, paragraph)
        return format_price(price.group())
    elif type_structure == "second":
        # If the price is not included on the same paragraph
        if not is_price_on_paragraph(paragraph):
            return "0"
        if re.search(checker_garantia_in_paragraph_pattern, paragraph):
            if re.search(checker_second_structure_price_in_table_format, paragraph):
                price = re.search(
                    price_second_structure_pdf_with_garantia_pattern_and_table_format,
                    paragraph,
                )
                return format_price(price.group(1))
            else:
                price = re.search(
                    price_second_structure_pdf_with_garantia_pattern, paragraph
                )
                return format_price(price.group(1))
        else:
            price = re.search(
                price_second_structure_pdf_without_garantia_pattern, paragraph
            )
            return format_price(price.group(1))


def format_price(price):
    return float(
        price.replace(".", "").replace(",", ".").replace(" ", "").replace("€", "")
    )


def is_price_on_paragraph(paragraph):
    result = re.search(checker_second_structure_price_not_in_the_paragraph, paragraph)
    return result


list_of_lands = get_pliego_relevant_info(
    "https://www.hacienda.gob.es/DGPatrimonio/Gesti%C3%B3n%20Patrimonial/subastas/DEH_LEON/Pliego-subasta-rusticas-2024.pdf"
)
for counter, info in enumerate(list_of_lands):
    print(f"The {counter+1} has the next info: {info}")

""" print(
    read_pdf(
        "https://www.hacienda.gob.es/DGPatrimonio/Gesti%C3%B3n%20Patrimonial/subastas/DEH_LEON/Pliego-subasta-rusticas-2024.pdf"
    )
) """
