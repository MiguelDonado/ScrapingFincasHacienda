from auctions import get_all_auctions_urls
from auction import get_url_pliego_pdf
from pliegopdf import get_pliego_info
from get_info_land import get_whole_info_land


def main():
    auctions = get_all_auctions_urls()
    auctions_pliegos_urlpdf = [get_url_pliego_pdf(auction) for auction in auctions]
    # The relevant info extracted from the pliego is (ref_catastral, price)
    print(
        "\n\n########################################################################################################\n"
    )
    auctions_pliegos_info = [
        get_pliego_info(pliego_url) for pliego_url in auctions_pliegos_urlpdf
    ]
    # To filter the errors
    # The auctions_pliegos_info has the next structure:
    """ [
            [auction
                (lote
                    [ref catastral],
                    'price'                
                ),
            ],
        ]
    1. List of lists. 
        2. Each inner list (auction), contains multiple tuples
            3. Each tuple contains two elements.
                4. The first is a list of referencias catastrales of the lote
                5. The second is a float price
    """

    filtered_auctions_pliegos_info = [
        (ref, price)
        for auction_info in auctions_pliegos_info
        for ref, price in auction_info
        if price != "ERROR"
    ]
    print(
        f"\nThe following lands are gonna be searched on the catastro page to get more info.\n{filtered_auctions_pliegos_info}"
    )
    print(
        "\n############################ LANDS INFO ####################################################################\n"
    )
    # Get the info from the filtered list of lands
    lands_info = [
        get_whole_info_land(*auction_info)
        for auction_info in filtered_auctions_pliegos_info
    ]


if __name__ == "__main__":
    main()
