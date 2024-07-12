# Contains several functions, that are all used when calling the function get_pliego_pdf. Given the PDF that contains the list of lands in auction, it extracts
# the ref_catastral and the price

import requests
import regex
import pdfplumber
import io
import Hacienda.constants as const
import logging


def get_pliego_info(url_pdf, i_delegation):
    try:
        text = read_pdf(url_pdf)
        paragraphs = get_desired_paragraphs(text)
        if paragraphs[0] == "first_structure":
            final_data = [
                get_desired_information("first", paragraph)
                for paragraph in paragraphs[1]
            ]
        elif paragraphs[0] == "second_structure":
            final_data = [
                get_desired_information("second", paragraph)
                for paragraph in paragraphs[1]
            ]
        # If the prices are not included on the same paragraph, but all together at the end.
        if final_data[0][1] == "0":
            prices = regex.findall(const.PRICE_WHEN_IS_NOT_IN_PARAGRAPH, text)
            prices = [format_price(price) for price in prices]
            ref_catastrales = [item[0] for item in final_data]
            final_data = list(zip(ref_catastrales, prices))

        lotes = [
            {"refs_catastrales": refs, "precio": price} for refs, price in final_data
        ]
        for i_lote, lote in enumerate(lotes, 1):
            # When the processing of a lote gives some error, it returns (None, None)
            if lote["refs_catastrales"] == None:
                logging.warning(
                    f"{i_delegation} - {i_lote} - X Failed to process the lote {i_lote}"
                )
            else:
                logging.info(
                    f"{i_delegation} - {i_lote} - X {''.join(lote['refs_catastrales'])}, {lote['precio']}"
                )
        lotes = [lote for lote in lotes if lote["refs_catastrales"]]
        return lotes
    except Exception as e:
        logging.error(
            f"{i_delegation} - X - X Failed to process Pliego PDF using get_pliego_info function: {e}"
        )
        return None


def read_pdf(url_pdf):
    response = requests.get(url_pdf)
    pdf_content = response.content
    pdf_file = io.BytesIO(pdf_content)
    with pdfplumber.open(pdf_file) as pdf:
        text_pages = [page.extract_text() for page in pdf.pages]
    all_text_file = " ".join(text_pages)
    return all_text_file


def get_desired_paragraphs(all_text_pdf):
    if regex.search(const.CHECKER_SECOND_STRUCTURE_PATTERN, all_text_pdf):
        return "second_structure", regex.findall(
            const.SECOND_PARAGRAPHS_PATTERN, all_text_pdf
        )
    else:
        return "first_structure", regex.findall(
            const.FIRST_PARAGRAPHS_PATTERN, all_text_pdf
        )


def get_desired_information(type_structure, paragraph):
    try:
        return (get_ref_catastral(paragraph), get_precio(type_structure, paragraph))
    except AttributeError:
        return (None, None)


def get_ref_catastral(paragraph):
    ref_catastrales = regex.findall(const.REF_CATASTRAL_PATTERN, paragraph)
    if len(ref_catastrales) == 1:
        return ref_catastrales
    elif len(ref_catastrales) > 1:
        return ref_catastrales
    else:
        raise AttributeError("There is not a valid referencia catastral")


def get_precio(type_structure, paragraph):
    if type_structure == "first":
        price = regex.search(const.PRICE_FIRST_STRUCTURE_PDF_PATTERN, paragraph)
        return format_price(price.group())
    elif type_structure == "second":
        # If the price is not included on the same paragraph
        if not is_price_on_paragraph(paragraph):
            return "0"
        if regex.search(const.CHECKER_GARANTIA_IN_PARAGRAPH_PATTERN, paragraph):
            if regex.search(
                const.CHECKER_SECOND_STRUCTURE_PRICE_IN_TABLE_FORMAT, paragraph
            ):
                price = regex.search(
                    const.PRICE_SECOND_STRUCTURE_PDF_WITH_GARANTIA_PATTERN_AND_TABLE_FORMAT,
                    paragraph,
                )
                return format_price(price.group(1))
            else:
                price = regex.search(
                    const.PRICE_SECOND_STRUCTURE_PDF_WITH_GARANTIA_PATTERN, paragraph
                )
                final_price = price.group(1) or price.group(2)
                return format_price(final_price)
        else:
            price = regex.search(
                const.PRICE_SECOND_STRUCTURE_PDF_WITHOUT_GARANTIA_PATTERN, paragraph
            )
            return format_price(price.group(1))


def format_price(price):
    return float(
        price.replace(".", "").replace(",", ".").replace(" ", "").replace("€", "")
    )


def is_price_on_paragraph(paragraph):
    result = regex.search(
        const.CHECKER_SECOND_STRUCTURE_PRICE_IN_THE_PARAGRAPH, paragraph
    )
    return result


""" list_of_lands = get_pliego_info(
    "https://www.hacienda.gob.es/DGPatrimonio/Gestión%20Patrimonial/subastas/DEH-CADIZ/01%20-%20Pliego%20de%20condiciones.pdf.xsig.pdf"
)
for counter, info in enumerate(list_of_lands):
    print(f"The {counter+1} has the next info: {info}") """

""" print(
    read_pdf(
        "https://www.hacienda.gob.es/DGPatrimonio/Gesti%C3%B3n%20Patrimonial/subastas/DEH-ILLES_BALEARS/PLIEGO-CONDICIONES_%20Subasta10jul2024.pdf"
    )
) """
