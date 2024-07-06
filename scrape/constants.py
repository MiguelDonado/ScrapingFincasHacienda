import regex


######################################## HACIENDA #######################################################
# Number of delegations are 57 in total
NUMBER_OF_DELEGATIONS = (
    12  # This number is for testing purposes, so it only run on a few provinces.
)
BASE_URL_HACIENDA = "https://www.hacienda.gob.es"
DELEGATION_URL = (
    "https://www.hacienda.gob.es/es-ES/Areas%20Tematicas/Patrimonio%20del%20Estado/"
    "Gestion%20Patrimonial%20del%20Estado/Paginas/Subastas/ListadoSubastasConcursos.aspx?"
    "den=&nat=&dels={code}%3B"
)
PLIEGO_PATTERN = regex.compile(".*liego.*", flags=regex.IGNORECASE)
ANEXO_PATTERN = regex.compile(".*nexo.*", flags=regex.IGNORECASE)

####################################### CATASTRO ########################################################
BASE_REF_CATASTRAL_URL = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?del={provincia}&mun={municipio}&RefC={ref_catastral}"
BASE_URL_SEARCH_CATASTRO = (
    "https://www1.sedecatastro.gob.es/Cartografia/mapa.aspx?buscar=S"
)

###################################### CORREOS ##########################################################
BASE_URL_CORREOS = "https://www.correos.es/es/es/herramientas/codigos-postales/detalle"
