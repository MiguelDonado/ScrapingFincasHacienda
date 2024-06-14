import requests
from bs4 import BeautifulSoup
from support_regex import auction_href_pattern
import regex

NUMBER_OF_DELEGATIONS = 8
delegation_url = (
    "https://www.hacienda.gob.es/es-ES/Areas%20Tematicas/Patrimonio%20del%20Estado/"
    "Gestion%20Patrimonial%20del%20Estado/Paginas/Subastas/ListadoSubastasConcursos.aspx?"
    "den=&nat=&dels={code}%3B"
)


def get_all_auctions_urls():
    all_auction_anchors = []
    for number in range(1, NUMBER_OF_DELEGATIONS):
        final_delegation_url = delegation_url.format(code=number)
        html_text = requests.get(final_delegation_url)
        soup = BeautifulSoup(html_text.text, "lxml")
        anchors_delegation = soup.find_all("a")
        auctions_anchors_delegation = [
            anchor.get("href")
            for anchor in anchors_delegation
            if regex.search(auction_href_pattern, anchor.get("href"))
        ]
        all_auction_anchors.extend(auctions_anchors_delegation)
    return all_auction_anchors
