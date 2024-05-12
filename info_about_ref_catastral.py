import re
import requests
from bs4 import BeautifulSoup

ref_catastral_url = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?del={provincia}&mun={municipio}&RefC={ref_catastral}"


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
    html_text = requests.get(url)
    # soup = BeautifulSoup(html_text.text, "lxml")
    # anchors = soup.find_all("a")


print(
    get_info_about_url_ref_catastral(
        "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?del=15&mun=090&RefC=15090A507018480000AY"
    )
)
