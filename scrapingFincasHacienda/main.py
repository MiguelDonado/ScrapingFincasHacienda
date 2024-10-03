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

# GOOGLE MAPS
from GoogleMaps.GoogleMaps import GoogleMaps

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
                # (mandatory for next steps) | data_correos = {"cp", "province", "locality"}
                # (optional for next steps) | report_data_land = {"ath","denominacion_ath","agrupacion_cultivo","agrupacion_municipio","number_buildings","slope","fls"}
                # (optional for next steps) | value_land = float
                # (optional for next steps) | data_ine_population = {"population_now","population_before","porcentual_variation"}
                # (optional for next steps) | data_ine_transmisiones = {"transactions_now","transactions_before","variation"}
                # (optional for next steps) | data_two_directions = {"car": {"distance","time"}, "foot": {"distance","time"}}
                # (optional for next steps) | data_sabi = df with 61 columns
                # (optional for next steps) | data_two_directions = {"car": {"distance","time"}, "foot": {"distance","time"}}

                # 5.1) CATASTRO CLASS
                try:
                    land_object = Catastro(delegation, i_lote, i_land, land)
                    info_land = land_object.get_data()
                    data_land = info_land["data"]
                    coordinates_land = info_land["coordinates"]
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
                one_direction = GoogleMaps(delegation, i_lote, i_land, land, coordinates_land)
                one_direction.get_data_one_direction()  # Just takes a screenshot, doesn't return anything

                # 5.4) CATASTRO_REPORT CLASS
                report = CatastroReport(
                    delegation, i_lote, i_land, land, data_land["clase"]
                )
                info_report = report.get_data()
                report_data_land = info_report["data"]
                value_land = info_report["value"]

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
                if not data_sabi:
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
                        coordinates_land,   # 'to'
                        enterprise_direction, # 'from'
                        enterprise['Nombre'] # 'enterprise'
                    )
                    # Variable that holds a dictionary with 2 keys, each one holds another dictionary with 2 keys.
                    # {"car": {"distance","time"}, "foot": {"distance","time"}}
                    data_two_directions = two_directions.get_data_two_directions()
                    full_data_two_directions.append(
                        {
                            enterprise['Código NIF']: {'data':data_two_directions,'screenshot':0} # path_to_screenshot
                    }
                    )
                    break
                # This is the info that I'll introduce in the db for each land.
                full_data_land = {
                    # --------- MANDATORY ------------ #
                    "delegation": delegation,
                    "auction_url": auction,
                    "auction_pdf": 0,#path_to_downloaded_pdf
                    "lote_number":i_lote,
                    "referencia_catastral":land,
                    "price":data_lote["price"],
                    "localizacion": data_land["localizacion"],
                    "clase": data_land["clase"],
                    "uso": data_land["uso"],
                    "aprovechamiento": data_land["cultivo_aprovechamiento"],
                    "coordenadas": coordinates_land,
                    "codigo_postal": data_correos["cp"],
                    "province": data_correos["province"],
                    "locality": data_correos["locality"],
                    # --------- OPTIONAL ------------- #
                    "screenshot": 0,#path_to_screenshot,
                    "ath_number": report_data_land["ath"],
                    "ath_name": report_data_land["denominacion_ath"], 
                    "agrupacion_municipio": report_data_land["agrupacion_municipio"],
                    "number_buildings": report_data_land["number_buildings"],
                    "slope": report_data_land["slope"],
                    "fls": report_data_land["fls"],
                    "catastro_value": value_land,
                    "population_now":data_ine_population["population_now"],
                    "population_before":data_ine_population["population_before"],
                    "rusticas_transactions_now":data_ine_transmisiones["transactions_now"],
                    "rusticas_transactions_before":data_ine_transmisiones["transactions_before"],
                    "empresas": data_sabi,
                    "empresas_fincas": full_data_two_directions
                    }
                break
            break


if __name__ == "__main__":
    main()
