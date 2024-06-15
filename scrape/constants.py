import regex

NUMBER_OF_DELEGATIONS = 12
DELEGATION_URL = (
    "https://www.hacienda.gob.es/es-ES/Areas%20Tematicas/Patrimonio%20del%20Estado/"
    "Gestion%20Patrimonial%20del%20Estado/Paginas/Subastas/ListadoSubastasConcursos.aspx?"
    "den=&nat=&dels={code}%3B"
)
BASE_REF_CATASTRAL_URL = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?del={provincia}&mun={municipio}&RefC={ref_catastral}"
pliego_pattern = regex.compile(".*liego.*", flags=regex.IGNORECASE)
anexo_pattern = regex.compile(".*nexo.*", flags=regex.IGNORECASE)
