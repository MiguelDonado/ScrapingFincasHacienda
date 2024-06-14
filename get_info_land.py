import re
import traceback
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning  # type: ignore

# When doing a request to the catastro web it gaves me an error because of SSL certificate. So i have to make a request without SSL certificate verification, and because of that
# i also have to deactivate a warning message that's displayed because of making a request without SSL certificate.
requests.packages.urllib3.disable_warnings(
    InsecureRequestWarning
)  # Disable SSL warning

base_ref_catastral_url = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?del={provincia}&mun={municipio}&RefC={ref_catastral}"


def get_whole_info_land(ref_catastral, price):
    try:
        # Si el lote solo contiene una referencia catastral
        if len(ref_catastral) == 1:
            ref_catastral_url = get_url_ref_catastral(ref_catastral[0])
            m2, *additional_info = get_info_about_url_ref_catastral(ref_catastral_url)
            price_per_m2 = round(price / m2, 3)
            whole_info_land = (
                [ref_catastral[0]]
                + additional_info
                + [m2, ref_catastral_url, price, price_per_m2]
            )
            return whole_info_land
        # Si el lote contiene mas de una referencia catastral
        elif len(ref_catastral) > 1:
            whole_info_lands = []
            total_m2 = 0
            for ref in ref_catastral:
                ref_catastral_url = get_url_ref_catastral(ref)
                m2, *additional_info = get_info_about_url_ref_catastral(
                    ref_catastral_url
                )
                temp = [ref] + additional_info + [ref_catastral_url]
                whole_info_lands.append(temp)
                total_m2 += m2
            price_per_m2 = round(price / total_m2, 3)
            whole_info_lands = list(zip(*whole_info_lands))
            whole_info_lands = ["; ".join(field) for field in whole_info_lands]
            whole_info_lands.insert(7, total_m2)
            whole_info_lands.insert(10, price_per_m2)
            return whole_info_lands
    except:
        return [ref_catastral, price] + [""] * 8


def get_url_ref_catastral(ref_catastral):

    provincia = ref_catastral[0:2]
    municipio = ref_catastral[2:5]

    ref_catastral_url = base_ref_catastral_url.format(
        provincia=provincia,
        municipio=municipio,
        ref_catastral=ref_catastral,
    )
    return ref_catastral_url


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
    metros_cuadrados = float(
        (
            datosinmueble.find("span", string="Superficie gráfica")
            .find_next_sibling()
            .find("label")
            .get_text()
        )
        .replace(" m2", "")
        .replace(".", "")
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
