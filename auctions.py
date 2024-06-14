import requests
from bs4 import BeautifulSoup
from support_regex import auction_href_pattern
import regex

# NUMBER_OF_DELEGATIONS = 57
NUMBER_OF_DELEGATIONS = 12
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
        auction_anchors_delegation = [
            a.get("href") for a in soup.find_all("a", href=auction_href_pattern)
        ]
        if auction_anchors_delegation:
            print(
                f"\no The following auction has been retrieved: {auction_anchors_delegation}"
            )
        all_auction_anchors.extend(auction_anchors_delegation)
    return all_auction_anchors


get_all_auctions_urls()
