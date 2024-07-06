# Function used to extract all the url of the available auctions.

import requests
from bs4 import BeautifulSoup
import processpdf.constants as processpdf_const
import regex
import scrape.constants as const


def get_all_auctions_urls():
    all_auction_anchors = []
    for number in range(1, const.NUMBER_OF_DELEGATIONS):
        final_delegation_url = const.DELEGATION_URL.format(code=number)
        html_text = requests.get(final_delegation_url)
        soup = BeautifulSoup(html_text.text, "lxml")
        auction_anchors_delegation = [
            a.get("href")
            for a in soup.find_all("a", href=processpdf_const.AUCTION_HREF_PATTERN)
        ]
        if auction_anchors_delegation:
            print(
                f"\no The following auction has been retrieved: {auction_anchors_delegation}"
            )
        all_auction_anchors.extend(auction_anchors_delegation)
    return all_auction_anchors
