import regex

DB_NAME = "FincasProject.db"
# Search line by line, and take everything before data type
COLUMNS_PATTERN = regex.compile(r".+\"\s")
EMPRESAS_HEADERS = """
    "Nombre" TEXT,
    "Código NIF" TEXT,
    "Localidad" TEXT, 
    "País" TEXT,
    "Código consolidación" TEXT,
    "Ultimo año disponible" TEXT,
    "Provincia" TEXT,
    "Importe neto de la cifra de negocios mil EUR Últ. año disp." NUMERIC,
    "Importe neto de la cifra de negocios mil EUR Año - 1" NUMERIC,
    "Total activo (A + B) mil EUR Últ. año disp." NUMERIC,
    "Total activo (A + B) mil EUR Año - 1" NUMERIC,
    "Número empleados Últ. año disp." NUMERIC,
    "Número empleados Año - 1" NUMERIC,
    "Código primario CNAE 2009" NUMERIC,
    "Literal código CNAE 2009 primario" NUMERIC,
    "Resultado del Ejercicio mil EUR Últ. año disp." NUMERIC,
    "Resultado del Ejercicio mil EUR Año - 1" NUMERIC,
    "Ingresos de explotación mil EUR Últ. año disp." NUMERIC,
    "Ingresos de explotación mil EUR Año - 1" NUMERIC,
    "Fondos propios mil EUR Últ. año disp." NUMERIC,
    "Fondos propios mil EUR Año - 1" NUMERIC,
    "Result. ordinarios antes Impuestos mil EUR Últ. año disp." NUMERIC,
    "Result. ordinarios antes Impuestos mil EUR Año - 1" NUMERIC,
    "Rentabilidad económica (%) % Últ. año disp." NUMERIC,
    "Rentabilidad económica (%) % Año - 1" NUMERIC,
    "Rentabilidad financiera (%) % Últ. año disp." NUMERIC,
    "Rentabilidad financiera (%) % Año - 1" NUMERIC,
    "Liquidez general % Últ. año disp." NUMERIC,
    "Liquidez general % Año - 1" NUMERIC,
    "Endeudamiento (%) % Últ. año disp." NUMERIC,
    "Endeudamiento (%) % Año - 1" NUMERIC,
    "EBITDA mil EUR Últ. año disp." NUMERIC,
    "EBITDA mil EUR Año - 1" NUMERIC,
    "Cash flow mil EUR Últ. año disp." NUMERIC,
    "Cash flow mil EUR Año - 1" NUMERIC,
    "Margen de beneficio (%) % Últ. año disp." NUMERIC,
    "Margen de beneficio (%) % Año - 1" NUMERIC,
    "Período de cobro (días) días Últ. año disp." NUMERIC,
    "Período de cobro (días) días Año - 1" NUMERIC,
    "Período de crédito (días) días Últ. año disp." NUMERIC,
    "Período de crédito (días) días Año - 1" NUMERIC,
    "Rotación de las existencias % Últ. año disp." NUMERIC,
    "Rotación de las existencias % Año - 1" NUMERIC,
    "Coeficiente de solvencia (%) % Últ. año disp." NUMERIC,
    "Coeficiente de solvencia (%) % Año - 1" NUMERIC,
    "Beneficio por empleado mil Últ. año disp." NUMERIC,
    "Beneficio por empleado mil Año - 1" NUMERIC,
    "Ingresos de explotación por empleado mil Últ. año disp." NUMERIC,
    "Ingresos de explotación por empleado mil Año - 1" NUMERIC,
    "Coste medio de los empleados mil Últ. año disp." NUMERIC,
    "Coste medio de los empleados mil Año - 1" NUMERIC,
    "Costes de los trabajadores / Ingresos de explotación (%) % Últ. año disp." NUMERIC,
    "Costes de los trabajadores / Ingresos de explotación (%) % Año - 1" NUMERIC,
    "Ratio de solvencia % Últ. año disp." NUMERIC,
    "Ratio de solvencia % Año - 1" NUMERIC,
    "Calle" TEXT,
    "Código postal" TEXT,
"""

FINCA_HEADERS = """
    "referencia_catastral" TEXT NOT NULL,
    "localizacion" TEXT NOT NULL,
    "catastro_value" NUMERIC,
    "delegation_id" INTEGER NOT NULL,
    "agrupacion_cultivo_id" INTEGER,
    "locality_id" INTEGER NOT NULL,
    "lote_id" INTEGER NOT NULL,
    "clase_id" INTEGER NOT NULL,
    "uso_id" INTEGER NOT NULL,
    "aprovechamiento_id" INTEGER NOT NULL,
    "codigo_postal_id" INTEGER NOT NULL,
    "ath_id" INTEGER,
    "coordenadas" TEXT NOT NULL,
    "agrupacion_municipio" TEXT,
    "number_buildings" INTEGER,
    "slope" NUMERIC,
    "fls" NUMERIC,
    "ortofoto" BLOB NOT NULL,
    "kml" BLOB NOT NULL,
    "google_maps" BLOB NOT NULL,
    "report_catastro" BLOB,
    "datetime" NUMERIC NOT NULL DEFAULT CURRENT_TIMESTAMP,
"""
EMPRESAS_FINCAS_HEADERS = """
    "empresa_id" INTEGER NOT NULL,
    "finca_id" INTEGER NOT NULL,
    "distance_on_car" NUMERIC NOT NULL,
    "time_on_car" INTEGER NOT NULL,
    "distance_on_foot" NUMERIC NOT NULL,
    "time_on_foot" INTEGER NOT NULL,
    "route_screenshot" BLOB,
"""

ALLOWED_CLASES = ["rústico", "urbano", "de características especiales"]
ALLOWED_USOS = {
    "almacén, estac.": "Almacén-Estacionamiento",
    "comercial": "Comercial",
    "cultural": "Cultural",
    "ocio, hostelería": "Ocio y Hostelería",
    "industrial": "Industrial",
    "deportivo": "Deportivo",
    "oficinas": "Oficinas",
    "edif. singular": "Edificios singulares",
    "religioso": "Religioso",
    "espectáculos": "Espectáculos",
    "residencial": "Residencial",
    "sanidad, benefic,": "Sanidad y Beneficencia",
    "agrario": "Agrario",
    "suelo sin edif.": "Suelo sin edificar, obras de urbanización, jardinería y construcciones ruinosas",
    "industrial agr.": "Industrial agrario",
    "almacén agrario": "Almacén Agrario",
}
NUMBER_OF_DELEGATIONS = 56
DELEGATIONS = range(1, NUMBER_OF_DELEGATIONS + 1)
DELEGATION_MAPPING = {
    "1": "ARABA/ÁLAVA",
    "2": "ALBACETE",
    "3": "ALACANT/ALICANTE",
    "4": "ALMERÍA",
    "5": "ÁVILA",
    "6": "BADAJOZ",
    "7": "ILLES BALEARS",
    "8": "BARCELONA",
    "9": "BURGOS",
    "10": "CÁCERES",
    "11": "CÁDIZ",
    "12": "CASTELLÓ/CASTELLÓN",
    "13": "CIUDAD REAL",
    "14": "CÓRDOBA",
    "15": "CORUÑA, A",
    "16": "CUENCA",
    "17": "GIRONA",
    "18": "GRANADA",
    "19": "GUADALAJARA",
    "20": "GIPUZKOA",
    "21": "HUELVA",
    "22": "HUESCA",
    "23": "JAÉN",
    "24": "LEÓN",
    "25": "LLEIDA",
    "26": "RIOJA, LA",
    "27": "LUGO",
    "28": "MADRID",
    "29": "MÁLAGA",
    "30": "MURCIA",
    "31": "NAVARRA",
    "32": "OURENSE",
    "33": "OVIEDO",
    "34": "PALENCIA",
    "35": "PALMAS, LAS",
    "36": "PONTEVEDRA",
    "37": "SALAMANCA",
    "38": "SANTA CRUZ DE TENERIFE",
    "39": "CANTABRIA",
    "40": "SEGOVIA",
    "41": "SEVILLA",
    "42": "SORIA",
    "43": "TARRAGONA",
    "44": "TERUEL",
    "45": "TOLEDO",
    "46": "VALÈNCIA/VALENCIA",
    "47": "VALLADOLID",
    "48": "BIZKAIA",
    "49": "ZAMORA",
    "50": "ZARAGOZA",
    "51": "CARTAGENA",
    "52": "GIJÓN",
    "53": "JEREZ DE LA FRONTERA",
    "54": "VIGO",
    "55": "CEUTA",
    "56": "MELILLA",
}