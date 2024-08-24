# HACIENDA
import Hacienda.constants as const
from Hacienda.auction_delegation import has_auction
from Hacienda.pliego_url import get_pliego
from Hacienda.data_pdf import get_lotes_data

# CATASTRO
from Catastro.catastro import Catastro
from Catastro.report import CatastroReport

# CORREOS
from Correos.correos import Correos

# INE
from INE.ine_population import InePopulation
from INE.ine_num_transmisiones_fincas_rusticas import IneNumTransmisionesFincasRusticas

# SABI
from Sabi.sabi import Sabi

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
            i_lote = lote["id"]
            data_lote = lote["data"]
            # 5) For each land on the lote
            for i_land, land in enumerate(data_lote["refs"], 1):

                # LAND VARIABLES THAT CONTAINS RELEVANT DATA:
                # (mandatory for next steps) | data_land = {"localizacion","clase", "uso", "cultivo_aprovechamiento"}
                # (mandatory for next steps) | coordinates_land = string
                # (optional for next steps) | value_land = float
                # (optional for next steps) | report_data_land = {"ath","denominacion_ath","agrupacion_cultivo","agrupacion_municipio","number_buildings","slope","fls"}
                # (mandatory for next steps) | data_correos = {"cp", "province", "locality"}
                # (optional for next steps) | data_ine_population = {"population_now","population_before","porcentual_variation"}
                # (optional for next steps) | data_ine_transmisiones = {"transactions_now","transactions_before","variation"}

                # 5.1) CATASTRO CLASS
                try:
                    land_object = Catastro(delegation, i_lote, i_land, land)
                    info_land = land_object.get_data()
                    data_land = info_land["data"]
                    coordinates_land = info_land["coordinates"]
                except Exception:
                    continue

                # 5.2) CATASTRO_REPORT CLASS
                report = CatastroReport(
                    delegation, i_lote, i_land, land, data_land["clase"]
                )
                info_report = report.get_data()
                value_land = info_report["value"]
                report_data_land = info_report["data"]

                # 5.3) CORREOS_CLASS
                correos = Correos(
                    delegation, i_lote, i_land, land, data_land["localizacion"]
                )
                data_correos = correos.get_data()

                # If direction couldn't be extracted using correos webpage.
                if not data_correos["cp"]:
                    continue

                # 5.4) INE_POPULATION CLASS
                ine_population = InePopulation(
                    delegation,
                    i_lote,
                    i_land,
                    land,
                    data_land["localizacion"],
                    data_correos["locality"],
                )
                data_ine_population = ine_population.get_data()

                # 5.5) INE_NUMBER_TRANSMISIONES CLASS
                if data_land["clase"] == "Rústico":
                    ine_transmisiones = IneNumTransmisionesFincasRusticas(
                        delegation, i_lote, i_land, land, data_correos["cp"]
                    )
                    data_ine_transmisiones = ine_transmisiones.get_data()

                # 5.6) SABI CLASS
                sabi = Sabi(delegation, i_lote, i_land, land, data_correos["cp"])
                # The method below returns a dataframe
                # 'Nombre', "Calle", "Código postal"
                data_sabi = sabi.get_data()
                break
            break


if __name__ == "__main__":
    main()
