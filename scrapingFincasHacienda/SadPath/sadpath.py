import logging
import sys

import logger_config
import requests
import SadPath.constants as const
from GoogleMaps.GoogleMaps import GoogleMaps

logger = logging.getLogger(__name__)

id_land = (
    const.data_test["delegation"],
    const.data_test["i_lote"],
    const.data_test["i_land"],
    const.data_test["land"],
)


def check_status_code(url):
    response = requests.get(url)
    if response.status_code != 200:
        # Log
        msg = f"URL: '{url}' has been requested. Expected status code 200, but got {response.status_code}"
        logger.error(
            f"{msg}",
            exc_info=True,
        )
        sys.exit()
    else:
        msg = f"URL: '{url}' has been requested. Get back status code 200."
        logger.info(f"{msg}")


def check_catastro():
    check_status_code(const.BASE_REF_CATASTRAL_URL)
    check_status_code(const.BASE_URL_SEARCH_CATASTRO)
    check_status_code(const.BASE_URL_REPORT_CATASTRO)


def check_correos():
    check_status_code(const.BASE_URL_CORREOS)


def check_googlemaps():
    check_status_code(const.BASE_URL_GOOGLE_MAPS)


def check_hacienda():
    check_status_code(const.BASE_URL_HACIENDA)
    check_status_code(const.DELEGATION_URL)


def check_iberpix():
    check_status_code(const.BASE_URL_IBERPIX)


def check_ine():
    check_status_code(const.BASE_URL_INE)
    check_status_code(const.POBLACION_URL_INE)

    """path_googlemaps_land = GoogleMaps(
        *id_land, const.data_test["coordinates_land"]
    ).get_data_one_direction()"""


def check_webpages_work():
    msg = f"################## SAD PATH CHECKING ##################"
    logger.info(f"{msg}")
    check_catastro()
    check_correos()
    check_googlemaps()
    check_hacienda()
    check_iberpix()
    check_ine()
