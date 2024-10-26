from pathlib import Path

BASE_URL_IBERPIX = "https://www.ign.es/iberpix/"
DOWNLOAD_DIR = Path("../data/iberpix").resolve()
SUFFIX_FILENAME_CURVAS_NIVEL = "_mapa_curvas_nivel.png"
SUFFIX_FILENAME_LIDAR = "_mapa_lidar.png"
SUFFIX_FILENAME_USOS_SUELO = "_mapa_usos_suelo.png"
SUFFIX_FILENAME_HIDROGRAFIA = "_mapa_hidrografia.png"

##### LAYERS ######
HIDROGRAFIA = "https://servicios.idee.es/wms-inspire/hidrografia?"
ORTOFOTOS_PROVISIONALES = "https://wms-pnoa.idee.es/pnoa-provisionales?"
