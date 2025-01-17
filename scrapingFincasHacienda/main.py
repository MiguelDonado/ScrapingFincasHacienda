import pickle
import sys

import Hacienda.constants as const
from Catastro.catastro import Catastro
from Catastro.report import CatastroReport
from Correos.correos import Correos
from Database.helpers import insert_land_data, is_auction_id_old
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
            i_lote = lote["id"]
            data_lote = lote["data"]

            # If a lote of an auction couldnt be properly proccesed, continue
            if not data_lote["refs"]:
                continue

            for i_land, land in enumerate(data_lote["refs"], 1):

                # Tuple containing key arguments
                # *id_land = to unpack the tuple into separate arguments
                id_land = (delegation, i_lote, i_land, land)

                # 7.1) CATASTRO CLASS
                try:
                    info_land = Catastro(*id_land).get_data()
                    keys = ["data", "coordinates", "ortofoto", "kml"]
                    data_land, coordinates_land, path_ortofoto_land, path_kml_land = [
                        info_land[key] for key in keys
                    ]
                except Exception:
                    continue

                # 7.2) CORREOS_CLASS
                data_correos = Correos(*id_land, data_land["localizacion"]).get_data()

                # 7.3) GOOGLE_MAPS CLASS
                path_googlemaps_land = GoogleMaps(
                    *id_land, coordinates_land
                ).get_data_one_direction()

                # 7.4) CATASTRO_REPORT CLASS
                info_report = CatastroReport(*id_land, data_land["clase"]).get_data()
                keys = ["data", "value", "path"]
                report_data_land, value_land, path_report_land = [
                    info_report[key] for key in keys
                ]

                # 7.5) INE_POPULATION CLASS
                data_ine_population = InePopulation(
                    *id_land, data_land["localizacion"], data_correos["locality"]
                ).get_data()

                # 7.6) INE_NUMBER_TRANSMISIONES CLASS
                data_ine_transmisiones = IneNumTransmisionesFincasRusticas(
                    *id_land,
                    data_correos["cp"],
                    data_land["clase"],
                ).get_data()

                # 7.7) IBERPIX CLASS
                info_iberpix = Iberpix(
                    *id_land, path_kml_land, data_land["clase"]
                ).get_data()
                data_usos_suelo, paths_iberpix = info_iberpix.values()
                keys = ["curvas_nivel", "lidar", "usos_suelo", "ortofoto_hidrografia"]
                (
                    fullpath_mapa_curvas_nivel,
                    fullpath_mapa_lidar,
                    fullpath_usos_suelo,
                    fullpath_ortofoto_hidrografia,
                ) = [paths_iberpix[key] for key in keys]

                # 7.8) SABI CLASS
                # 'data_sabi' contains a df with 23 columns and up to <n> enterprises
                data_sabi = Sabi(*id_land, data_correos["cp"], n_emp=1).get_data()

                # 7.9) GOOGLE MAPS CLASS
                # 'full_data_two_directions' contain data up to <n> enterprises given a land
                full_data_two_directions = full_get_data_two_directions(
                    *id_land, coordinates_land, data_sabi
                )

                # This is the info that I'll introduce in the db for each land.
                full_data_land = {
                    ############### MANDATORY ############
                    "electronical_id": id_auction,
                    "delegation": delegation,
                    "lote_number": i_lote,
                    "referencia_catastral": land,
                    "price": data_lote["price"],
                    "localizacion": data_land["localizacion"],
                    "municipio": data_land["municipio"],
                    "clase": data_land["clase"],
                    "uso": data_land["uso"],
                    "aprovechamiento": data_land["cultivo"],
                    "coordenadas": coordinates_land,
                    "codigo_postal": data_correos["cp"],
                    "province": data_correos["province"],
                    "locality": data_correos["locality"],
                    ############### OPTIONAL ##############
                    # '**' This notation is used to expand a dictionary
                    "ath_number": report_data_land["ath"],
                    "ath_name": report_data_land["denominacion_ath"],
                    "agrupacion_cultivo": report_data_land["agrupacion_cultivo"],
                    "agrupacion_municipio": report_data_land["agrupacion_municipio"],
                    "number_buildings": report_data_land["number_buildings"],
                    "slope": report_data_land["slope"],
                    "fls": report_data_land["fls"],
                    "population_now": data_ine_population["population_now"],
                    "population_before": data_ine_population["population_before"],
                    "rusticas_transactions_now": data_ine_transmisiones[
                        "transactions_now"
                    ],
                    "rusticas_transactions_before": data_ine_transmisiones[
                        "transactions_before"
                    ],
                    "catastro_value": value_land,
                    "empresas": data_sabi,
                    "empresas_fincas": full_data_two_directions,
                    "usos_suelo": data_usos_suelo,
                    ############### FILES ##############
                    **convert_paths(
                        auction_pdf_path,
                        path_ortofoto_land,
                        path_kml_land,
                        path_googlemaps_land,
                        path_report_land,
                        fullpath_mapa_curvas_nivel,
                        fullpath_mapa_lidar,
                        fullpath_usos_suelo,
                        fullpath_ortofoto_hidrografia,
                    ),
                }

                # Save to a pickle file
                with open("data.pkl", "wb") as pkl_file:
                    pickle.dump(full_data_land, pkl_file)

                sys.exit()
                insert_land_data(full_data_land)
                # ######## For debugging purposes ########
                # save_python_object_to_file(data_sabi)


if __name__ == "__main__":
    main()
