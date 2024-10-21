import sys

import Hacienda.constants as const
from Catastro.catastro import Catastro
from Catastro.report import CatastroReport
from Correos.correos import Correos
from Database.models import insert_land_data, is_old
from GoogleMaps.GoogleMaps import GoogleMaps
from Hacienda.auction_delegation import has_auction
from Hacienda.data_pdf import get_auction_id, get_lotes_data
from Hacienda.pliego_url import get_pliego
from INE.ine_num_transmisiones_fincas_rusticas import IneNumTransmisionesFincasRusticas
from INE.ine_population import InePopulation
from Sabi.sabi import Sabi


def get_value(object, key=None):
    if object:
        if not key:
            return object
        else:
            return object[key]
    else:
        return None


def convert_path_to_str(path):
    if not path:
        return None
    else:
        return str(path)


def main():
    for delegation in const.DELEGATIONS:

        # 1) Search on hacienda website if there's any auction.
        auction = has_auction(delegation)
        if not auction:
            continue

        # 2) Get the pdf that contains the list of lands.
        #    get_pliego function returns a dictionary with two keys. {"url":value, "path": value}
        auction_pdf = get_pliego(auction, delegation)
        if not auction_pdf:
            continue
        # Get the contents of the return dictionary
        auction_pdf_url, auction_pdf_path = auction_pdf.values()

        """3) Get the ref_catastral and price from the lands.
            o The variable lotes is a list of dictionaries.
                o Each dictionary represents a lote, it has two keys.
                    1) Id
                    2) Data (nested dictionary with two keys {refs, price})
                        1) Refs_catastrales: Holds a list of refs.
                        2) Price: Holds the price for the lote.
            Example:
            [ {1, {[ref1, ref2], price}}, {2, {[ref1, ref2], price}},... ]
               ____________________
              |       LOTE 1       | """

        id_auction = get_auction_id(auction_pdf_url, delegation, auction)
        # If this auction is already store in the database, continue to the next one
        if not id_auction:
            continue
        lotes = get_lotes_data(auction_pdf_url, delegation)
        # When the function 'get_lotes_data' fails to process the auction_pdf_url
        # it returns 'None'
        if not lotes:
            continue

        # 4) For each lote in auction
        for lote in lotes:

            skip_outer = False  # Initialize skip_outer at the start

            i_lote = lote["id"]
            data_lote = lote["data"]
            # 5) For each land on the lote
            for i_land, land in enumerate(data_lote["refs"], 1):
                """For the first land of the auction I'm gonna check if it's already
                on the database, if so, then the auction should be skipped because
                its not new, its the second, third round of an existing auction.
                If the land is not on the database then the auction is new, and there
                is no sense in checking for more lands of the auction if they are already
                on the database."""

                # Check first_land of auction
                if i_land == 1:
                    is_auction_old = is_old(land)
                    if is_auction_old:
                        skip_outer = True
                        break
                # LAND VARIABLES THAT CONTAINS RELEVANT DATA:
                # (mandatory for next steps) | data_land = {"localizacion","province", "municipio", "clase", "uso", "cultivo"}
                # (mandatory for next steps) | coordinates_land = string
                # (mandatory for next steps) | data_correos = {"cp", "province", "locality"}
                # (optional for next steps) | report_data_land = {"ath","denominacion_ath","agrupacion_cultivo","agrupacion_municipio","number_buildings","slope","fls"}
                # (optional for next steps) | value_land = float
                # (optional for next steps) | data_ine_population = {"population_now","population_before"}
                # (optional for next steps) | data_ine_transmisiones = {"transactions_now","transactions_before"}
                # (optional for next steps) | data_two_directions = {"car": {"distance","time"}, "foot": {"distance","time"}}
                # (optional for next steps) | data_sabi = df with 61 columns
                # (optional for next steps) | data_two_directions = {"car": {"distance","time"}, "foot": {"distance","time"}}

                # FILES THAT ARE DOWNLOADED:
                # (mandatory) | auction_pdf_path (saved in /data/auction/some_name.pdf) | get_pliego()
                # (mandatory) | path_ortofoto_land (saved in /data/catastro/some_name.pdf) | Catastro.get_data()
                # (mandatory) | path_kml_land (saved in /data/catastro/some_name.kml) | Catastro.get_data()
                # (mandatory) | path_googlemaps_land (saved in /data/googlemaps/ref_catast.png) | Google_Maps.get_one_direction()
                # (optional, only for rusticas) | path_report_land (saved in /data/report/some_name.pdf) | CatastroReport.get_data()
                # (mandatory) | data_two_directions['path'] (saved in /data/googlemaps/ref_catast-name_enterprise.png) | Google_Maps.get_data_two_directions()

                # 5.1) CATASTRO CLASS
                try:
                    land_object = Catastro(delegation, i_lote, i_land, land)
                    info_land = land_object.get_data()
                    data_land = info_land["data"]
                    coordinates_land = info_land["coordinates"]
                    path_ortofoto_land = info_land["ortofoto"]
                    path_kml_land = info_land["kml"]
                except Exception:
                    continue

                # 5.2) CORREOS_CLASS
                correos = Correos(
                    delegation, i_lote, i_land, land, data_land["localizacion"]
                )
                data_correos = correos.get_data()

                # If direction couldn't be extracted using correos webpage.
                if not data_correos["cp"]:
                    continue

                # 5.3) GOOGLE_MAPS CLASS
                one_direction = GoogleMaps(
                    delegation, i_lote, i_land, land, coordinates_land
                )
                path_googlemaps_land = one_direction.get_data_one_direction()

                # 5.4) CATASTRO_REPORT CLASS
                report = CatastroReport(
                    delegation, i_lote, i_land, land, data_land["clase"]
                )
                info_report = report.get_data()
                report_data_land = info_report["data"]
                value_land = info_report["value"]
                path_report_land = info_report["path"]

                # 5.5) INE_POPULATION CLASS
                ine_population = InePopulation(
                    delegation,
                    i_lote,
                    i_land,
                    land,
                    data_land["localizacion"],
                    data_correos["locality"],
                )
                data_ine_population = ine_population.get_data()

                # 5.6) INE_NUMBER_TRANSMISIONES CLASS
                if data_land["clase"] == "Rústico":
                    ine_transmisiones = IneNumTransmisionesFincasRusticas(
                        delegation, i_lote, i_land, land, data_correos["cp"]
                    )
                    data_ine_transmisiones = ine_transmisiones.get_data()

                # 5.7) SABI CLASS
                sabi = Sabi(delegation, i_lote, i_land, land, data_correos["cp"])
                # The method below returns a dataframe with 61 columns.
                # Some of the columns are 'Nombre', "Calle", "Código postal", "Localidad"
                data_sabi = sabi.get_data()

                # If data couldn't be extracted using sabi (mandatory for the next step)
                if data_sabi is None:
                    continue

                # 5.8) GOOGLE MAPS CLASS
                # Dictionary that will hold the data for the 25 enterprises given a land
                full_data_two_directions = []
                for _, enterprise in data_sabi.iterrows():
                    enterprise_direction = f"{enterprise['Calle']}. {enterprise["Código postal"]} {enterprise["Localidad"]}"
                    two_directions = GoogleMaps(
                        delegation,
                        i_lote,
                        i_land,
                        land,
                        coordinates_land,  # 'to'
                        enterprise_direction,  # 'from'
                        enterprise["Nombre"],  # 'enterprise'
                    )
                    # Variable that holds a dictionary with 2 keys, each one holds another dictionary with 2 keys.
                    # {"car": {"distance","time"}, "foot": {"distance","time"}}
                    data_two_directions = two_directions.get_data_two_directions()
                    full_data_two_directions.append(
                        {"cif": enterprise["Código NIF"], "data": data_two_directions}
                    )

                # This is the info that I'll introduce in the db for each land.
                full_data_land = {
                    # --------- MANDATORY ------------ #
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
                    # --------- OPTIONAL ------------- #
                    "ath_number": get_value(report_data_land, "ath"),
                    "ath_name": get_value(report_data_land, "denominacion_ath"),
                    "agrupacion_cultivo": get_value(
                        report_data_land, "agrupacion_cultivo"
                    ),
                    "agrupacion_municipio": get_value(
                        report_data_land, "agrupacion_municipio"
                    ),
                    "number_buildings": get_value(report_data_land, "number_buildings"),
                    "slope": get_value(report_data_land, "slope"),
                    "fls": get_value(report_data_land, "fls"),
                    "catastro_value": get_value(value_land),
                    "population_now": get_value(data_ine_population, "population_now"),
                    "population_before": get_value(
                        data_ine_population, "population_before"
                    ),
                    "rusticas_transactions_now": get_value(
                        data_ine_transmisiones, "transactions_now"
                    ),
                    "rusticas_transactions_before": get_value(
                        data_ine_transmisiones, "transactions_before"
                    ),
                    "empresas": data_sabi,
                    "empresas_fincas": full_data_two_directions,
                    # --------- FILES ------------- #
                    "auction_pdf_path": convert_path_to_str(auction_pdf_path),
                    "path_ortofoto_land": convert_path_to_str(path_ortofoto_land),
                    "path_kml_land": convert_path_to_str(path_kml_land),
                    "path_googlemaps_land": convert_path_to_str(path_googlemaps_land),
                    "path_report_land": convert_path_to_str(path_report_land),
                }
                insert_land_data(full_data_land)
                sys.exit()
            if skip_outer:
                break  # Exit the middle loop


if __name__ == "__main__":
    main()
