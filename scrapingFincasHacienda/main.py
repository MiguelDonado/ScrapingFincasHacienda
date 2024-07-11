from Hacienda.auction_delegation import has_auction_url
from Hacienda.auction_pliego_url import get_url_pliego_pdf
from Hacienda.auction_get_data_pdf import get_pliego_info
from Catastro.catastro import Catastro
from Catastro.catastro_report import CatastroReport

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
    for index_delegation in range(1, const.NUMBER_OF_DELEGATIONS + 1):
        #      1) Search on hacienda website if there's any auction.
        auction = has_auction_url(index_delegation)
        if not auction:
            continue
        #      2) Get the pdf that contains the list of lands.
        auction_pdf = get_url_pliego_pdf(auction, index_delegation)
        #      3) Get the ref_catastral and price from the lands
        auction_pdf_info = get_pliego_info(auction_pdf, index_delegation)
        if not auction_pdf_info:
            continue
        #      4) For each lote in auction
        for index_lote, lote in enumerate(auction_pdf_info):
            # lote[0] = ref catastrales
            # lote[1] = price
            #      5) For each land on the lote
            for index_land, land in enumerate(lote[0]):
                try:
                    #   5.1) Scrape data from Catastro
                    catastro_land = Catastro(land)
                    catastro_land.land_first_page()
                    catastro_land.search()
                    #       5.1.1) The variable data_land will hold data scraped from the Catastro web:
                    #           {localizacion, clase, uso, cultivo_aprovechamiento}
                    data_land = catastro_land.get_info_about_search()
                    logging.info(
                        f"{index_delegation}.\t\t{index_lote} - {index_land}: {data_land}"
                    )
                except Exception as e:
                    logging.error(
                        f"{index_delegation}.\t\t{index_lote} - {index_land}. An error occurred while scraping data with Catastro: {e}"
                    )

                try:
                    #       5.1.2) Download the KML file
                    catastro_land.go_to_otros_visores()
                    catastro_land.download_kml()
                    logging.info(
                        f"{index_delegation}.\t\t{index_lote} - {index_land}: The kml has been downloaded successfully"
                    )
                except Exception as e:
                    logging.error(
                        f"{index_delegation}.\t\t{index_lote} - {index_land}. An error occurred while downloading KML: {e}"
                    )

                try:
                    #   5.2) Download PDF report from a different Catastro webpage and scrape reference_value
                    catastro_land_report = CatastroReport(land, data_land["clase"])
                    catastro_land_report.land_first_page()
                    catastro_land_report.close_cookies()
                    catastro_land_report.land_query_value_page()
                    catastro_land_report.access_with_dni()
                    catastro_land_report.select_date_and_property()
                    #   5.2.1) Get the reference_value
                    reference_value = catastro_land_report.get_reference_value_amount()
                    logging.info(
                        f"{index_delegation}.\t\t{index_lote} - {index_land}: Reference_value = {reference_value}"
                    )
                except Exception as e:
                    logging.error(
                        f"{index_delegation}.\t\t{index_lote} - {index_land}. An error occurred while scraping the reference_value using the CatastroReport class: {e}"
                    )

                try:
                    #   5.2.2) Get the PDF report, only when the land is "Rústico", in the rest of the cases
                    #   the pdf is different, and it hasn't relevant data.
                    #   The logic is implemented inside the method
                    report_path = catastro_land_report.get_reference_value_report()
                    if not report_path:
                        msg = "The pdf is not relevant in this case."
                    else:
                        msg = "The pdf has been downloaded successfully"
                        logging.info(
                            f"{index_delegation}.\t\t{index_lote} - {index_land}: {msg}"
                        )
                except Exception as e:
                    logging.error(
                        f"{index_delegation}.\t\t{index_lote} - {index_land}. An error occurred while downloading the reference_value using the CatastroReport class: {e}"
                    )

                try:
                    #   5.2.3) Process the PDF report
                    if report_path:
                        report_data = catastro_land_report.process_report(report_path)
                        logging.info(
                            f"{index_delegation}.\t\t{index_lote} - {index_land}: {report_data}"
                        )
                    else:
                        logging.info(
                            f"{index_delegation}.\t\t{index_lote} - {index_land}: Since no PDF, no PDF has been processed"
                        )
                except Exception as e:
                    logging.error(
                        f"{index_delegation}.\t\t{index_lote} - {index_land}. An error occurred while processing the reference_value using the CatastroReport class: {e}"
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
