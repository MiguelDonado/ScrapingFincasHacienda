import re

auction_href_pattern = re.compile("^https://.+Estado/Paginas/Subastas/.+")
# The first segment of the regex is for "fincas rusticas", the second for "fincas urbanas"
ref_catastral_pattern = re.compile(
    r"(?:\d{2}\d{3}[A-Z]\d{3}\d{5}\d{4}[A-Z]{2}|\d{7}[A-Z]{2}\d{4}[A-Z]\d{4}[A-Z]{2})"
)
price_pattern = re.compile(r"(?<=\s)[\d\.,]+\s€")
paragraphs_pattern = re.compile(
    "^(?:Rústica|Urbana).*?Referencia\sCatastral:[\w ]+$",
    flags=re.DOTALL | re.MULTILINE,
)


# https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?del=15&mun=90&RefC=15090A507018480000AY
