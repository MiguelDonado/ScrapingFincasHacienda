from Hacienda.auction_delegation import has_auction_url
from Hacienda.auction_pliego_url import get_url_pliego_pdf
from Hacienda.auction_get_data_pdf import get_pliego_info
from Catastro.catastro import Catastro

# from scrapingFincasHacienda.Hacienda.to_rename import get_url_pliego_pdf
# from scrapingFincasHacienda.Hacienda.hacienda_pliegopdf import get_pliego_info
import Hacienda.constants as const
import logging

# Set up basic configuration for logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log",
    filemode="a",
)


def main():
    # In total there are 57 delegations. So for each one of them we're going to do the next:
    for i in range(1, const.NUMBER_OF_DELEGATIONS + 1):
        #      1) Search on hacienda website if there's any auction.
        auction = has_auction_url(i)
        if not auction:
            continue
        #      2) Get the pdf that contains the list of lands.
        auction_pdf = get_url_pliego_pdf(auction, i)
        #      3) Get the ref_catastral and price from the lands
        auction_pdf_info = get_pliego_info(auction_pdf, i)
        if not auction_pdf_info:
            continue
        #      4) For each lote in auction -> for each land on the lote
        #      -> get the info that appears on the specific catastro webpage
        #      -> {localizacion, clase, uso, cultivo_aprovechamiento}
        for index_lote, lote in enumerate(auction_pdf_info):
            # lote[0] = ref catastrales
            # lote[1] = price
            # Si el lote esta compuesto por mas de una finca,
            # PARA CADA FINCA HAZ LO SIGUIENTE
            for index_land, land in enumerate(lote[0]):
                try:
                    catastro_land = Catastro(land)
                    catastro_land.land_first_page()
                    catastro_land.search()
                    data_land = catastro_land.get_info_about_search()
                    logging.info(f"{i}.\t\t{index_lote}: {data_land}")
                    catastro_land.go_to_otros_visores()
                    catastro_land.download_kml()
                    catastro_land.rename_kml(land)
                    logging.info(
                        f"{i}.\t\t{index_land}: The kml has been downloaded successfully"
                    )
                except Exception as e:
                    logging.error(
                        f"{i}. An error occurred with the Catastro class: {e}"
                    )

    '''auctions = get_all_auctions_urls()
    auctions_pliegos_urlpdf = [get_url_pliego_pdf(auction) for auction in auctions]
    # The relevant info extracted from the pliego is (ref_catastral, price)
    print(
        "########################################################################################################"
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
        f"The following lands are gonna be searched on the catastro page to get more info.{filtered_auctions_pliegos_info}"
    )
    print(
        "############################ LANDS INFO ####################################################################"
    )
    # Get the info from the filtered list of lands
    lands_info = [
        get_whole_info_land(*auction_info)
        for auction_info in filtered_auctions_pliegos_info
    ]
    print(lands_info)'''


if __name__ == "__main__":
    main()
