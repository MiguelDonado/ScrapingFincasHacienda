import re

auction_href_pattern = re.compile("^https://.+Estado/Paginas/Subastas/.+")
# The first segment of the regex is for "fincas rusticas", the second for "fincas urbanas", the third is for a strange case
ref_catastral_pattern = re.compile(
    r"^.*Referen\s?cias?\s+Catastral(?:es)?:?\s+(\d{2}\d{3}[A-Z]\d{3}\d{5}\d{4}[A-Z]{2}|\d{7}[A-Z]{2}\d{4}[A-Z]\d{4}[A-Z]{2}|\d{7}[A-Z]{2}\d{4}[A-Z])",
    flags=re.MULTILINE | re.IGNORECASE,
)

# Checkers to know the type of pdf we are analyzing
checker_second_structure_pattern = re.compile(
    r"^(?!.*c.digo|.*€|.*euro).*(?:LOTE|BIEN)\s+.*\d+(?!%)",
    flags=re.MULTILINE | re.IGNORECASE,
)

checker_garantia_in_paragraph_pattern = re.compile(
    r"^.*(garant.a|fianza)",
    flags=re.MULTILINE | re.IGNORECASE,
)

checker_second_structure_price_in_table_format = re.compile(
    r"^(Subasta\sPrimera\sSegunda\sTercera\sCuarta|SUBASTA 1ª 2ª 3ª 4ª)",
    flags=re.MULTILINE | re.IGNORECASE,
)

checker_second_structure_price_not_in_the_paragraph = re.compile(r"\d+[\d\.]*,\d\d")

# This is the regular expression that is able to handle the pliego pdf that has the next structure (tables)
# Example: https://www.hacienda.gob.es/DGPatrimonio/Gesti%C3%B3n%20Patrimonial/subastas/DEH%20OURENSE/Pliego_Sub.30_abril_2024.pdf
first_paragraphs_pattern = re.compile(
    r"^(?:Rústica|Urbana).*?Referencia\sCatastral:[\w ]+$",
    flags=re.DOTALL | re.MULTILINE,
)
price_first_structure_pdf_pattern = re.compile(r"(?<=\s)[\d\.,]+\s€")
# This is the regular expression that is able to handle the pliego pdf that has the next structure (paragraphs)
# Example: https://www.hacienda.gob.es/DGPatrimonio/Gesti%C3%B3n%20Patrimonial/subastas/DEH_TERUEL/Pliego%20de%20condiciones%20subasta.pdf
second_paragraphs_pattern = re.compile(
    r"^(?!.*c.digo|.*€|.*euro).*(?:LOTE|BIEN)\s+.*\d+(?!%)(?:.|\n)*?(?=^(?!.*c.digo|.*€|.*euro).*(?:LOTE|BIEN)\s+.*\d+(?!%)|^Segunda[:\.]\s)",
    flags=re.MULTILINE | re.IGNORECASE,
)

###### (On the second pdf structure). If have "garantia" on the paragraph:
price_second_structure_pdf_with_garantia_pattern = re.compile(
    r"^.*(?:licitaci.n|salida).*?(\d+[\d\.,]*)\s*?(?:euros|€)",
    flags=re.MULTILINE | re.IGNORECASE,
)

###### (On the second pdf structure). If have "garantia" on the paragraph and the price is on table format:
price_second_structure_pdf_with_garantia_pattern_and_table_format = re.compile(
    r"^.*(?:licitaci.n)\s+.*?(\d+[\d\.,]*)\s",
    flags=re.MULTILINE | re.IGNORECASE,
)


###### (On the second pdf structure). If doesn't have "garantia" on the paragraph:
price_second_structure_pdf_without_garantia_pattern = re.compile(
    r"^.*Subasta:\s+(\d+[\d\.,]*)\s+Euros", flags=re.MULTILINE | re.IGNORECASE
)

#### (On the second pdf structure). If price is not included on the paragraph but at the end of the file.
price_when_is_not_in_paragraph = re.compile(
    r"^\d+\s.*subasta.*?(\d+[\d\.,]*)", flags=re.MULTILINE | re.IGNORECASE
)

# https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?del=15&mun=90&RefC=15090A507018480000AY
