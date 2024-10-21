import pickle

from GoogleMaps.GoogleMaps import GoogleMaps


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


def full_get_data_two_directions(
    delegation, i_lote, i_land, land, coordinates_land, data_sabi
):
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
    return full_data_two_directions


def get_optional_values(report_data_land, data_ine_population, data_ine_transmisiones):
    return {
        "ath_number": get_value(report_data_land, "ath"),
        "ath_name": get_value(report_data_land, "denominacion_ath"),
        "agrupacion_cultivo": get_value(report_data_land, "agrupacion_cultivo"),
        "agrupacion_municipio": get_value(report_data_land, "agrupacion_municipio"),
        "number_buildings": get_value(report_data_land, "number_buildings"),
        "slope": get_value(report_data_land, "slope"),
        "fls": get_value(report_data_land, "fls"),
        "population_now": get_value(data_ine_population, "population_now"),
        "population_before": get_value(data_ine_population, "population_before"),
        "rusticas_transactions_now": get_value(
            data_ine_transmisiones, "transactions_now"
        ),
        "rusticas_transactions_before": get_value(
            data_ine_transmisiones, "transactions_before"
        ),
    }


def convert_paths(
    auction_pdf_path,
    path_ortofoto_land,
    path_kml_land,
    path_googlemaps_land,
    path_report_land,
):
    return {
        "auction_pdf_path": convert_path_to_str(auction_pdf_path),
        "path_ortofoto_land": convert_path_to_str(path_ortofoto_land),
        "path_kml_land": convert_path_to_str(path_kml_land),
        "path_googlemaps_land": convert_path_to_str(path_googlemaps_land),
        "path_report_land": convert_path_to_str(path_report_land),
    }


def save_python_object_to_file(data):
    with open("data.pkl", "wb") as file:
        pickle.dump(data, file)


def read_python_object_from_file():
    with open("data.pkl", "rb") as file:
        data = pickle.load(file)
        print(data)
    return data


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
