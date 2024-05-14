import re
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning  # type: ignore

# When doing a request to the catastro web it gaves me an error because of SSL certificate. So i have to make a request without SSL certificate verification, and because of that
# i also have to deactivate a warning message that's displayed because of making a request without SSL certificate.
requests.packages.urllib3.disable_warnings(
    InsecureRequestWarning
)  # Disable SSL warning

ref_catastral_url = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?del={provincia}&mun={municipio}&RefC={ref_catastral}"


def get_whole_info_land(ref_catastral, price):
    catastro_url = get_url_ref_catastral(ref_catastral)
    additional_info = get_info_about_url_ref_catastral(catastro_url)
    return [ref_catastral, price] + additional_info


def get_url_ref_catastral(ref_catastral):

    provincia = ref_catastral[0:2]
    municipio = ref_catastral[2:5]

    final_ref_catastral_url = ref_catastral_url.format(
        provincia=provincia,
        municipio=municipio,
        ref_catastral=ref_catastral,
    )
    return final_ref_catastral_url


def get_info_about_url_ref_catastral(url):
    html_text = requests.get(url, verify=False)
    soup = BeautifulSoup(html_text.text, "lxml")
    datosinmueble = soup.find("div", id="datosinmueble")
    municipio, provincia = (
        datosinmueble.find("span", string="Localización")
        .find_next_sibling()
        .find("label")
        .get_text()
        .rsplit(". ")[1]
        .replace(")", "")
        .split(" (")
    )
    uso = (
        datosinmueble.find("span", string="Uso principal")
        .find_next_sibling()
        .find("label")
        .get_text()
    )
    metros_cuadrados = (
        datosinmueble.find("span", string="Superficie gráfica")
        .find_next_sibling()
        .find("label")
        .get_text()
    )
    cultivo_aprovechamiento = (
        datosinmueble.find("div", id="ctl00_Contenido_divtblCultivos")
        .find("table", id="ctl00_Contenido_tblCultivos")
        .find_all("tr")[-1]
        .find_all("td")[1]
        .get_text()
    )

    google_maps_url = (
        "https://www1.sedecatastro.gob.es/Cartografia/BuscarParcelaInternet.aspx?refcat="
        + url.rsplit("=", 1)[1]
    )

    return [
        metros_cuadrados,
        municipio,
        provincia,
        cultivo_aprovechamiento,
        uso,
        google_maps_url,
    ]
