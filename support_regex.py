import re

auction_href_pattern = re.compile("^https://.+Estado/Paginas/Subastas/.+")
# The first segment of the regex is for "fincas rusticas", the second for "fincas urbanas"
ref_catastral_pattern = re.compile(
    r"(?:\d{2}\d{3}[A-Z]\d{3}\d{5}\d{4}[A-Z]{2}|\d{7}[A-Z]{2}\d{4}[A-Z]\d{4}[A-Z]{2})"
)
price_pattern = re.compile(r"(?<=\s)[\d\.,]+\s€")

# This is the regular expression that is able to handle the pliego pdf that has the next structure
# https://www.hacienda.gob.es/DGPatrimonio/Gesti%C3%B3n%20Patrimonial/subastas/DEH%20OURENSE/Pliego_Sub.30_abril_2024.pdf
first_paragraphs_pattern = re.compile(
    "^(?:Rústica|Urbana).*?Referencia\sCatastral:[\w ]+$",
    flags=re.DOTALL | re.MULTILINE,
)

# This is the regular expression that is able to handle the pliego pdf that has the next structure
# https://www.hacienda.gob.es/DGPatrimonio/Gesti%C3%B3n%20Patrimonial/subastas/DEH_TERUEL/Pliego%20de%20condiciones%20subasta.pdf
second_paragraphs_pattern = re.compile(
    "^LOTE Nº \d+:.*?(?=(?:^LOTE Nº \d+|^Segunda:\s|^SEGUNDA:\s))",
    flags=re.DOTALL | re.MULTILINE,
)

# https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?del=15&mun=90&RefC=15090A507018480000AY
