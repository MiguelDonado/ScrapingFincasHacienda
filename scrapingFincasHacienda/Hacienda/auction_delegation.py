# Function used to extract the "newest" auction url of a delegation.

import requests
from bs4 import BeautifulSoup
import regex
import Hacienda.constants as const
import logging


# In some cases it could be more than one auction for the same delegation, there could be two reasons:
#      1) It's the 2nd, 3rd round for the same auction.
#      2) It's another auction.
# So, selecting only the first element of the array, it's a simple and pretty effective solution, because whenever I'm running the sript I'm selecting,
# always the newest url. Since the data extracted would be inserted into a database, it's OK if we don't get the older anchors, because they're older,
# they would be already on the database.
# The downside of this solution, is when it's run for the first time. The database is empty, so if there's more than one anchor and it's only selecting the last one,
# we'd be losing information for those links.
def has_auction_url(i_delegation):
    f_delegation_url = const.DELEGATION_URL.format(
        code=i_delegation
    )  # f_: Means formatted
    html_text = requests.get(f_delegation_url)
    soup = BeautifulSoup(html_text.text, "lxml")
    # Using the walrus operator. Initializes the variable, and checks if it's True
    if auction_anchor_delegation := soup.find("a", href=const.AUCTION_HREF_PATTERN):
        auction_href_delegation = auction_anchor_delegation.get("href")
        logging.info(
            f"{i_delegation} - X - X The auction has been retrieved: {auction_href_delegation}"
        )
        return auction_href_delegation
    else:
        logging.info(f"{i_delegation} - X - X No auctions available")
        return None
