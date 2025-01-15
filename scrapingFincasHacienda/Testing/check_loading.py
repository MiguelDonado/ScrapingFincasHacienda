import pickle
import pprint


def imprimir_datos_bonito(datos):
    # Utiliza pprint para manejar estructuras anidadas de manera legible
    pp = pprint.PrettyPrinter(indent=4, width=80)

    # Formatea los campos principales
    print("\n--- Información Principal ---")
    print(f"ID Electrónico: {datos.get('electronical_id', 'No disponible')}")
    print(f"Delegación: {datos.get('delegation', 'No disponible')}")
    print(f"Número de Lote: {datos.get('lote_number', 'No disponible')}")
    print(f"Referencia Catastral: {datos.get('referencia_catastral', 'No disponible')}")
    print(f"Precio: {datos.get('price', 'No disponible')} €")
    print(f"Localización: {datos.get('localizacion', 'No disponible')}")
    print(f"Municipio: {datos.get('municipio', 'No disponible')}")
    print(f"Clase: {datos.get('clase', 'No disponible')}")
    print(f"Uso: {datos.get('uso', 'No disponible')}")
    print(f"Coordenadas: {datos.get('coordenadas', 'No disponible')}")
    print(f"Código Postal: {datos.get('codigo_postal', 'No disponible')}")
    print(f"Provincia: {datos.get('province', 'No disponible')}")

    # Imprime detalles de la población
    print("\n--- Población ---")
    print(f"Población actual: {datos.get('population_now', 'No disponible')}")
    print(f"Población anterior: {datos.get('population_before', 'No disponible')}")

    # Imprime información de empresas
    print("\n--- Empresas ---")
    empresas = datos.get("empresas")
    if empresas is not None:
        print(empresas)
    else:
        print("No disponible")

    # Imprime detalles de empresas asociadas a fincas
    print("\n--- Empresas Fincas ---")
    empresas_fincas = datos.get("empresas_fincas", [])
    for empresa in empresas_fincas:
        print(f"CIF: {empresa.get('cif', 'No disponible')}")
        print("Datos:")
        pp.pprint(empresa.get("data", "No disponible"))

    # Imprime detalles de usos de suelo
    print("\n--- Usos del Suelo ---")
    pp.pprint(datos.get("usos_suelo", "No disponible"))

    # Imprime las rutas de archivos
    print("\n--- Rutas de Archivos ---")
    rutas = {
        "PDF de Subasta": datos.get("auction_pdf_path"),
        "Ortofoto": datos.get("path_ortofoto_land"),
        "KML": datos.get("path_kml_land"),
        "Google Maps": datos.get("path_googlemaps_land"),
    }
    for nombre, ruta in rutas.items():
        print(f"{nombre}: {ruta if ruta else 'No disponible'}")


# Supongamos que la variable 'datos' contiene el JSON proporcionado
# Puedes usar la función así:

###### LOADING TESTING DATA ######
#  Load it later
with open("Testing/data.pkl", "rb") as pkl_file:
    loaded_data = pickle.load(pkl_file)

imprimir_datos_bonito(loaded_data)
