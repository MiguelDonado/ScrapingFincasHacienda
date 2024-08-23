import os

BASE_REF_CATASTRAL_URL = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?del={provincia}&mun={municipio}&RefC={ref_catastral}"
BASE_URL_SEARCH_CATASTRO = (
    "https://www1.sedecatastro.gob.es/Cartografia/mapa.aspx?buscar=S"
)

DOWNLOAD_DIR = os.path.abspath("../data/catastro")
DOWNLOAD_DIR_REPORT = os.path.abspath("../data/report")
