from auctions import get_all_auctions_urls
from auction import get_url_pliego_pdf
from pliegopdf import get_pliego_relevant_info
from get_info_land import get_whole_info_land


def main():
    auctions = get_all_auctions_urls()
    auctions_pliegos_urlpdf = [get_url_pliego_pdf(auction) for auction in auctions]
    # The relevant info extracted from the pliego is (ref_catastral, price)
    print(
        "\n\n########################################################################################################\n"
    )
    auctions_pliegos_relevant_info = [
        get_pliego_relevant_info(pliego_url) for pliego_url in auctions_pliegos_urlpdf
    ]
    """final_info_lands = [
        get_whole_info_land(ref_catastral, price)
        for auction_pliego_relevant_info in auctions_pliegos_relevant_info
        for ref_catastral, price in auction_pliego_relevant_info
        if price != "ERROR"
    ]
    print(final_info_lands)"""


if __name__ == "__main__":
    main()
