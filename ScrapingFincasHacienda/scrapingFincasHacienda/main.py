import sys

import Hacienda.constants as const
from Catastro.catastro import Catastro
from Catastro.report import CatastroReport
from Correos.correos import Correos
from Database.models import insert_land_data, is_auction_id_old
from GoogleMaps.GoogleMaps import GoogleMaps
from Hacienda.auction_delegation import has_auction
from Hacienda.data_pdf import get_auction_id, get_lotes_data
from Hacienda.pliego_url import download_url_pliego_pdf, get_pliego
from Iberpix.iberpix import Iberpix
from INE.ine_num_transmisiones_fincas_rusticas import IneNumTransmisionesFincasRusticas
from INE.ine_population import InePopulation
from Sabi.sabi import Sabi
from utils import (
    convert_paths,
    full_get_data_two_directions,
    get_optional_values,
    is_auction_old,
    read_python_object_from_file,
    save_python_object_to_file,
)


def main():
    for delegation in const.DELEGATIONS:

        # 1) Search on hacienda website if there's any auction.
        if not (auction := has_auction(delegation)):
            continue

        # 2) Get the pdf that contains the list of lands. Returns url_pliego
        if not (auction_pdf_url := get_pliego(auction, delegation)):
            continue

        # 3) Get/build the auction unique identifier
        if not (id_auction := get_auction_id(auction_pdf_url, delegation, auction)):
            continue

        # 4) Check if id_auction is on db, if so continue
        if is_auction_id_old(delegation, id_auction):
            continue

        # 5) Download pdf from auction_pdf_url
        if not (
            auction_pdf_path := download_url_pliego_pdf(
                auction_pdf_url, delegation, auction
            )
        ):
            continue

        # 6) Extract ref_catastral and price.
        #       - 'lotes' is a list of dictionaries.
        #       - Each dictionary represents a lote with:
        #         1) Id
        #         2) Data (nested dictionary) with:
        #             - refs: List of refs
        #             - price: Price of the lote
        #     Example:
        #     [ {1, {[ref1, ref2], price}}, ...] """

        if not (lotes := get_lotes_data(auction_pdf_url, delegation)):
            continue

        # Check for the first 'available' land of the auction if its already stored on DB.
        if is_auction_old(delegation, lotes):
            continue

        for lote in lotes:
            skip_outer = False  # To handle already stored auctions
            i_lote = lote["id"]
            data_lote = lote["data"]

            # If a lote of an auction couldnt be properly proccesed, continue
            if not data_lote["refs"]:
                continue

            for i_land, land in enumerate(data_lote["refs"], 1):

                # 7.1) CATASTRO CLASS
                try:
                    land_object = Catastro(delegation, i_lote, i_land, land)
                    info_land = land_object.get_data()
                    data_land = info_land["data"]
                    coordinates_land = info_land["coordinates"]
                    path_ortofoto_land = info_land["ortofoto"]
                    path_kml_land = info_land["kml"]
                except Exception:
                    continue

                # 7.2) CORREOS_CLASS
                correos = Correos(
                    delegation, i_lote, i_land, land, data_land["localizacion"]
                )
                data_correos = correos.get_data()

                if not data_correos["cp"]:
                    continue

                # 7.3) GOOGLE_MAPS CLASS
                one_direction = GoogleMaps(
                    delegation, i_lote, i_land, land, coordinates_land
                )
                path_googlemaps_land = one_direction.get_data_one_direction()

                # 7.4) CATASTRO_REPORT CLASS
                report = CatastroReport(
                    delegation, i_lote, i_land, land, data_land["clase"]
                )
                info_report = report.get_data()
                report_data_land = info_report["data"]
                value_land = info_report["value"]
                path_report_land = info_report["path"]

                # 7.5) INE_POPULATION CLASS
                ine_population = InePopulation(
                    delegation,
                    i_lote,
                    i_land,
                    land,
                    data_land["localizacion"],
                    data_correos["locality"],
                )
                data_ine_population = ine_population.get_data()

                # 7.6) INE_NUMBER_TRANSMISIONES CLASS
                ine_transmisiones = IneNumTransmisionesFincasRusticas(
                    delegation,
                    i_lote,
                    i_land,
                    land,
                    data_correos["cp"],
                    data_land["clase"],
                )
                data_ine_transmisiones = ine_transmisiones.get_data()
                sys.exit()


#                 # 5.7) IBERPIX CLASS
#                 data_usos_suelo = None
#                 fullpath_mapa_curvas_nivel = None
#                 fullpath_mapa_lidar = None
#                 fullpath_usos_suelo = None
#                 fullpath_ortofoto_hidrografia = None

#                 if data_land["clase"] == "Rústico":
#                     iberpix = Iberpix(delegation, i_lote, i_land, land, path_kml_land)
#                     info_iberpix = iberpix.get_data()
#                     data_usos_suelo = info_iberpix["data"]

#                     paths_iberpix = info_iberpix["paths"]
#                     fullpath_mapa_curvas_nivel = paths_iberpix["curvas_nivel"]
#                     fullpath_mapa_lidar = paths_iberpix["lidar"]
#                     fullpath_usos_suelo = paths_iberpix["usos_suelo"]
#                     fullpath_ortofoto_hidrografia = paths_iberpix[
#                         "ortofoto_hidrografia"
#                     ]

#                 # 5.8) SABI CLASS
#                 sabi = Sabi(delegation, i_lote, i_land, land, data_correos["cp"])
#                 # 'data_sabi' contains a df with 61 columns and up to 25 enterprises
#                 data_sabi = sabi.get_data()
#                 if data_sabi is None:
#                     continue

#                 # 5.9) GOOGLE MAPS CLASS
#                 # 'full_data_two_directions' contain data for 25 enterprises given a land
#                 full_data_two_directions = full_get_data_two_directions(
#                     delegation, i_lote, i_land, land, coordinates_land, data_sabi
#                 )

#                 # This is the info that I'll introduce in the db for each land.
#                 full_data_land = {
#                     ############### MANDATORY ############
#                     "electronical_id": id_auction,
#                     "delegation": delegation,
#                     "lote_number": i_lote,
#                     "referencia_catastral": land,
#                     "price": data_lote["price"],
#                     "localizacion": data_land["localizacion"],
#                     "municipio": data_land["municipio"],
#                     "clase": data_land["clase"],
#                     "uso": data_land["uso"],
#                     "aprovechamiento": data_land["cultivo"],
#                     "coordenadas": coordinates_land,
#                     "codigo_postal": data_correos["cp"],
#                     "province": data_correos["province"],
#                     "locality": data_correos["locality"],
#                     ############### OPTIONAL ##############
#                     # '**' This notation is used to expand a dictionary
#                     **get_optional_values(
#                         report_data_land, data_ine_population, data_ine_transmisiones
#                     ),
#                     "catastro_value": value_land,
#                     "empresas": data_sabi,
#                     "empresas_fincas": full_data_two_directions,
#                     "usos_suelo": data_usos_suelo,
#                     ############### FILES ##############
#                     **convert_paths(
#                         auction_pdf_path,
#                         path_ortofoto_land,
#                         path_kml_land,
#                         path_googlemaps_land,
#                         path_report_land,
#                         fullpath_mapa_curvas_nivel,
#                         fullpath_mapa_lidar,
#                         fullpath_usos_suelo,
#                         fullpath_ortofoto_hidrografia,
#                     ),
#                 }
#                 save_python_object_to_file(full_data_land)
#                 insert_land_data(full_data_land)
#             if skip_outer:
#                 break  # To handle already stored auctions

if __name__ == "__main__":
    main()
