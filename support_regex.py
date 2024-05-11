import re

auction_href_pattern = re.compile("^https://.+Estado/Paginas/Subastas/.+")
rusticas_ref_catastral_pattern = re.compile(r"\d{2}\d{3}[A-Z]\d{3}\d{5}\d{4}[A-Z]{2}")
urbanas_ref_catastral_pattern = re.compile(r"\d{7}[A-Z]{2}\d{4}[A-Z]\d{4}[A-Z]{2}")
price = re.compile(r"(?<=\s)[\d\.,]+\s€")
paragraphs_ptrn = re.compile("(Rústica|Urbana):\s+")


# https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?del=15&mun=90&RefC=15090A507018480000AY
