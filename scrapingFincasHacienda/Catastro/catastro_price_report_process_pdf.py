# Function that given the price report pdf for a land, it extract multiple data using pdfplumber library

import pdfplumber


def get_data_pdf_report(file):
    # It'll return the text from the PDF file as one string
    with pdfplumber.open(file) as pdf:
        text_file = pdf.pages[0].extract_tables()
        ath, denominacion_ath, agrupacion_cultivo, one, agrupacion_municipio = (
            text_file[1][1]
        )
        two, three, four, number_buildings, slope, fls, *five = text_file[2][2]
        print(pdf.pages[0].extract_text())
    return [
        ath,
        denominacion_ath,
        agrupacion_cultivo,
        agrupacion_municipio,
        number_buildings,
        slope,
        fls,
    ]


print(get_data_pdf_report("../../data/pdf/InformePrecioCatastro.pdf"))
