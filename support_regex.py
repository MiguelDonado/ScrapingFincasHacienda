import regex

auction_href_pattern = regex.compile("^https://.+Estado/Paginas/Subastas/.+")
# The first segment of the regexgex is for "fincas rusticas", the second for "fincas urbanas", the third is for a strange case
ref_catastral_pattern = regex.compile(
    r"^"
    r"(?!.*(?:sur|norte|oeste|este))"
    r".*Referen\s?cias?\s+"
    r"(?:Catastral)?"
    r"(?:es)?"
    r"(?:\sde\sla\sfinca\srústica)?"
    r"(?:\ses\sla)?:?\s*"
    r"("
    r"\d{2}\d{3}[A-Z]\d{3}\d{5}\d{4}[A-Z]{2}|"
    r"\d{7}[A-Z]{2}\d{4}[A-Z]\d{4}[A-Z]{2}|"
    r"\d{7}[A-Z]{2}\d{4}[A-Z]"
    r")",
    flags=regex.MULTILINE | regex.IGNORECASE,
)

# Checkers to know the type of pdf we are analyzing
checker_second_structure_pattern = regex.compile(
    r"^(?!.*c.digo|.*Propiedad Horizontal|.*€|.*euro|.*(?:con|,|la) finca).*(?:LOTE|BIEN|(?-i:Finca)|(?-i:FINCA))\s(?:Nº)?.{0,10}?\d+(?!%)",
    flags=regex.MULTILINE | regex.IGNORECASE,
)

checker_garantia_in_paragraph_pattern = regex.compile(
    r"^.*(garant.a|fianza)",
    flags=regex.MULTILINE | regex.IGNORECASE,
)

checker_second_structure_price_in_table_format = regex.compile(
    r"^(Subasta\sPrimera\sSegunda\sTercera\sCuarta|SUBASTA 1ª 2ª 3ª 4ª)",
    flags=regex.MULTILINE | regex.IGNORECASE,
)

checker_second_structure_price_in_the_paragraph = regex.compile(r"\d+[\d\.]*,\d\d")

# This is the regular expression that is able to handle the pliego pdf that has the next structure (tables)
# Example: https://www.hacienda.gob.es/DGPatrimonio/Gesti%C3%B3n%20Patrimonial/subastas/DEH%20OURENSE/Pliego_Sub.30_abril_2024.pdf
first_paragraphs_pattern = regex.compile(
    r"^(?:Rústica|Urbana).*?Referencia\sCatastral:[\w ]+$",
    flags=regex.DOTALL | regex.MULTILINE,
)
price_first_structure_pdf_pattern = regex.compile(r"(?<=\s)[\d\.,]+\s€")
# This is the regular expression that is able to handle the pliego pdf that has the next structure (paragraphs)
# Example: https://www.hacienda.gob.es/DGPatrimonio/Gesti%C3%B3n%20Patrimonial/subastas/DEH_TERUEL/Pliego%20de%20condiciones%20subasta.pdf
common_regex = (
    r"(?<!.*(?:sur|norte|oeste|este|folio|linderos|c.digo|Propiedad Horizontal|(?:con|,|la) finca).*\n?.*)"
    r"(?:LOTE|BIEN|FINCA)\s(?:Nº)?\D{0,10}?\d{1,2}\D(?!%)"
)
second_paragraphs_pattern = regex.compile(
    (
        common_regex
        + r"(?:.|\n){30,}?"  # This is all that is in the middle of the paragraph
        + rf"(?:{common_regex}|^Segunda[:\.]\s)"
    ),
    flags=regex.MULTILINE | regex.IGNORECASE,
)
###### (On the second pdf structure). If have "garantia" on the paragraph:
price_second_structure_pdf_with_garantia_pattern = regex.compile(
    (
        r"^"
        r".*(?:licitaci.n|salida).*?"
        r"(?:(\d+[\d\.,]*)\s*?(?:euros|€)|\n.*?(\d+[\d\.,]*)\s*?(?:euros|€))"
    ),
    flags=regex.MULTILINE | regex.IGNORECASE,
)

###### (On the second pdf structure). If have "garantia" on the paragraph and the price is on table format:
price_second_structure_pdf_with_garantia_pattern_and_table_format = regex.compile(
    r"^.*(?:licitaci.n)\s+.*?(\d+[\d\.,]*)\s",
    flags=regex.MULTILINE | regex.IGNORECASE,
)


###### (On the second pdf structure). If doesn't have "garantia" on the paragraph:
price_second_structure_pdf_without_garantia_pattern = regex.compile(
    r"^.*(?:subasta|precio|precio\sde\ssalida).{0,10}?(\d+[\d\.,]*)\s+(?:Euros|€)",
    flags=regex.MULTILINE | regex.IGNORECASE,
)

#### (On the second pdf structure). If price is not included on the paragraph but at the end of the file.
price_when_is_not_in_paragraph = regex.compile(
    r"^\d+\s.*subasta.*?(\d+[\d\.,]*)", flags=regex.MULTILINE | regex.IGNORECASE
)

# https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?del=15&mun=90&RefC=15090A507018480000AY
