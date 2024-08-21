# HACIENDA
import Hacienda.constants as const
from Hacienda.auction_delegation import has_auction
from Hacienda.pliego_url import get_pliego
from Hacienda.data_pdf import get_lotes_data

"""

# CATASTRO
from Catastro.catastro import Catastro
from Catastro.catastro_report import CatastroReport

# CORREOS
from Correos.correos import Correos

# INE
from INE.ine_population import InePopulation
from INE.ine_num_transmisiones_fincas_rusticas import IneNumTransmisionesFincasRusticas

# from scrapingFincasHacienda.Hacienda.to_rename import get_url_pliego_pdf
# from scrapingFincasHacienda.Hacienda.hacienda_pliegopdf import get_pliego_info"""

import logging


def main():
    for delegation in const.DELEGATIONS:

        # 1) Search on hacienda website if there's any auction.
        auction = has_auction(delegation)
        if not auction:
            continue

        # 2) Get the pdf that contains the list of lands.
        auction_pdf = get_pliego(auction, delegation)
        if not auction_pdf:
            continue

        """3) Get the ref_catastral and price from the lands.
            o The variable auction_pdf_info is a list of dictionaries.
                o Each dictionary represents a lote, it has two keys.
                    1) Refs_catastrales: Holds a list of refs.
                    2) Price: Holds the price for the lote.
            Example:
            [ {[ref1, ref2], price}, {[ref1, ref2], price}, {[ref1, ref2],price} ]
               ____________________
              |       LOTE 1       |
                
            o The function get_pliego_info returns only the lotes that
              doesn't give an error """

        lotes = get_lotes_data(auction_pdf, delegation)

        # When the function 'get_lotes_data' fails to process the auction_pdf
        # it returns 'None'
        if not lotes:
            continue

        # 4) For each lote in auction
        for lote in lotes:
            # 5) For each land on the lote
            '''for i_land, ref in enumerate(lote["refs_catastrales"], 1):
                msg_header = f"{i_delegation} - {i_lote} - {i_land}"
                try:
                    #   5.1) Scrape data from Catastro
                    catastro_land = Catastro(ref)
                    catastro_land.land_first_page()
                    catastro_land.search()
                    #       5.1.1) The variable catastro_data will hold data scraped from the Catastro web:
                    #           {localizacion, clase, uso, cultivo_aprovechamiento}
                    catastro_data = catastro_land.get_info_about_search()
                    logging.info(f"{msg_header} {catastro_data}")
                except Exception as e:
                    error_msg = "Failed to scrape data '{localizacion, clase, uso, cultivo_aprovechamiento}' using Catastro class:"
                    logging.error(f"{msg_header} {error_msg} {e}")
                    continue

                try:
                    #       5.1.2) Download the KML file
                    catastro_land.go_to_otros_visores()
                    catastro_land.download_kml()
                    logging.info(
                        f"{msg_header} The kml has been downloaded successfully"
                    )
                except Exception as e:
                    error_msg = "Failed to download KML file using Catastro class:"
                    logging.error(f"{msg_header} {error_msg} {e}")
                    continue

                try:
                    #   5.2) Download PDF report from a different Catastro webpage and scrape reference_value
                    catastro_land_report = CatastroReport(ref, catastro_data["clase"])
                    catastro_land_report.land_first_page()
                    catastro_land_report.close_cookies()
                    catastro_land_report.land_query_value_page()
                    catastro_land_report.access_with_dni()
                    catastro_land_report.select_date_and_property()
                    #   5.2.1) Get the reference_value
                    catastro_land_value = (
                        catastro_land_report.get_reference_value_amount()
                    )
                    logging.info(
                        f"{msg_header} Reference_value = {catastro_land_value}"
                    )
                except Exception as e:
                    error_msg = "Failed to scrape data 'reference_value' using CatastroReport class:"
                    logging.error(f"{msg_header} {error_msg} {e}")
                    continue

                try:
                    #   5.2.2) Get the PDF report, only when the land is "Rústico", in the rest of the cases
                    #   the pdf is different, and it hasn't relevant data.
                    #   The logic is implemented inside the method
                    report_path = catastro_land_report.get_reference_value_report()
                    if not report_path:
                        msg = "The pdf is not relevant in this case."
                    else:
                        msg = "The pdf has been downloaded successfully"
                    logging.info(f"{msg_header} {msg}")
                except Exception as e:
                    error_msg = "Failed to download 'reference_value' report using CatastroReport class:"
                    logging.error(f"{msg_header}  {e}")

                try:
                    #   5.2.3) Process the PDF report
                    if report_path:
                        report_data = catastro_land_report.process_report(report_path)
                        logging.info(f"{msg_header} {report_data}")
                    else:
                        info_msg = f"Because it has the class '{catastro_data['clase']}', no PDF has been processed"
                        logging.info(f"{msg_header} {info_msg}")
                except Exception as e:
                    error_msg = "Failed to process the reference_value report using the CatastroReport class:"
                    logging.error(f"{msg_header} {error_msg} {e}")

                    #   5.3) Scrape data from Correos
                try:
                    correos_land = Correos(catastro_data["localizacion"])
                    correos_land.land_first_page()
                    correos_land.search()
                    correos_data = correos_land.get_info_about_search()
                    logging.info(f"{msg_header} {correos_data}")
                except Exception as e:
                    error_msg = "Failed to scrape data 'cp, province, locality' using Correos class"
                    logging.error(f"{msg_header} {error_msg} {e}")
                    continue

                    #   5.4) Scrape data from INE (using InePopulation class)
                try:
                    ine_population_land = InePopulation(
                        catastro_data["localizacion"], correos_data["locality"]
                    )
                    ine_population_land.land_first_page()
                    ine_population_land.search_population()
                    #       5.4.1) The variable ine_population_data will hold data scraped from the Ine web:
                    #           {population_now, population_before, porcentual_variation}
                    ine_population_data = ine_population_land.get_population()
                    logging.info(f"{msg_header} {ine_population_data}")
                except Exception as e:
                    error_msg = "Failed to scrape data 'population_now, population_before, variation' using InePopulation class"
                    logging.error(f"{msg_header} {error_msg} {e}")

                    #   5.5) Scrape data from INE (using IneNumTransmisionesFincasRusticas)
                    #   This scraping'll be done only if the finca is 'rustica'
                if catastro_data["clase"] == "Rústica":
                    cp_first_two_digits = correos_data["cp"][0:2]
                    try:
                        ine_num_transm = IneNumTransmisionesFincasRusticas(
                            cp_first_two_digits
                        )
                        ine_num_transm.land_first_page()
                        ine_num_transm.close_cookies()
                        ine_num_transm.choose_province()
                        ine_num_transm.choose_transaction_type()
                        ine_num_transm.choose_year()
                        ine_num_transm_data = ine_num_transm.get_results()
                        logging.info(f"{msg_header} {ine_num_transm_data}")
                    except:
                        error_msg = "Failed to scrape data 'transactions_now, transactions_before, variation' using IneNumTransmisionesFincasRusticas class"
                        logging.error(f"{msg_header} {error_msg} {e}")
                else:
                    info_msg = f"Because it has the class '{catastro_data['clase']}', no scraping has been performed using IneNumTransmisionesFincasRusticas class"
                    logging.info(f"{msg_header} {info_msg}")
    auctions = get_all_auctions_urls()
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
