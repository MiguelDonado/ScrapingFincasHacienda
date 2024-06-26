import requests
import regex
import pdfplumber
import io
from processpdf.constants import *


def get_pliego_info(url_pdf):
    print(f"\no The following document is being used to extract data {url_pdf}")
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
        prices = regex.findall(price_when_is_not_in_paragraph, text)
        prices = [format_price(price) for price in prices]
        ref_catastrales = [item[0] for item in final_data]
        final_data = list(zip(ref_catastrales, prices))
    print(
        f"\no The following information has been extracted from {url_pdf}\n{final_data}"
    )
    return final_data


def read_pdf(url_pdf):
    response = requests.get(url_pdf)
    pdf_content = response.content
    pdf_file = io.BytesIO(pdf_content)
    with pdfplumber.open(pdf_file) as pdf:
        text_pages = [page.extract_text() for page in pdf.pages]
    all_text_file = " ".join(text_pages)
    return all_text_file


def get_desired_paragraphs(all_text_pdf):
    if regex.search(checker_second_structure_pattern, all_text_pdf):
        return "second_structure", regex.findall(
            second_paragraphs_pattern, all_text_pdf
        )
    else:
        return "first_structure", regex.findall(first_paragraphs_pattern, all_text_pdf)


def get_desired_information(type_structure, paragraph):
    try:
        return (get_ref_catastral(paragraph), get_precio(type_structure, paragraph))
    except AttributeError:
        return ("ERROR", "ERROR")


def get_ref_catastral(paragraph):
    ref_catastrales = regex.findall(ref_catastral_pattern, paragraph)
    if len(ref_catastrales) == 1:
        return ref_catastrales
    elif len(ref_catastrales) > 1:
        return ref_catastrales
    else:
        raise AttributeError("There is not a valid referencia catastral")


def get_precio(type_structure, paragraph):
    if type_structure == "first":
        price = regex.search(price_first_structure_pdf_pattern, paragraph)
        return format_price(price.group())
    elif type_structure == "second":
        # If the price is not included on the same paragraph
        if not is_price_on_paragraph(paragraph):
            return "0"
        if regex.search(checker_garantia_in_paragraph_pattern, paragraph):
            if regex.search(checker_second_structure_price_in_table_format, paragraph):
                price = regex.search(
                    price_second_structure_pdf_with_garantia_pattern_and_table_format,
                    paragraph,
                )
                return format_price(price.group(1))
            else:
                price = regex.search(
                    price_second_structure_pdf_with_garantia_pattern, paragraph
                )
                final_price = price.group(1) or price.group(2)
                return format_price(final_price)
        else:
            price = regex.search(
                price_second_structure_pdf_without_garantia_pattern, paragraph
            )
            return format_price(price.group(1))


def format_price(price):
    return float(
        price.replace(".", "").replace(",", ".").replace(" ", "").replace("€", "")
    )


def is_price_on_paragraph(paragraph):
    result = regex.search(checker_second_structure_price_in_the_paragraph, paragraph)
    return result


""" list_of_lands = get_pliego_info(
    "https://www.hacienda.gob.es/DGPatrimonio/Gestión%20Patrimonial/subastas/DEH-CADIZ/01%20-%20Pliego%20de%20condiciones.pdf.xsig.pdf"
)
for counter, info in enumerate(list_of_lands):
    print(f"The {counter+1} has the next info: {info}") """

""" print(
    read_pdf(
        "https://www.hacienda.gob.es/DGPatrimonio/Gesti%C3%B3n%20Patrimonial/subastas/DEH_ZARAGOZA/Pliego%20condiciones%20subasta%202023_signed.pdf"
    )
) """
