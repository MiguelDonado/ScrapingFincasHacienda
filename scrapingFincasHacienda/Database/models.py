import sqlite3
from pathlib import Path

import Database.constants as const
import regex


def to_str(list):
    return ", ".join(f"'{item}'" for item in list)


def read_binary(path_binary_file):
    # If the path to the binary file is empty.
    # i.e. when a land doesnt have the report from the catastro
    # the path_report_catastro'll be None
    if not path_binary_file:
        return None
    with open(path_binary_file, "rb") as file:
        binary_file = file.read()
    return binary_file


def remove_file_from_filesystem(path):
    if path:
        file_path = Path(path)
        file_path.unlink()
    else:
        return None


class BaseDatabase:
    _shared_borg_state = {}

    # Implementing Borg Singleton
    # State sharing for different instances. https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj.__dict__ = cls._shared_borg_state
        return obj

    def __init__(self, db_name=const.DB_NAME):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row  # Enable named tuple access
        self.cursor = self.connection.cursor()

    def execute_query(self, query, params=None):
        with self.connection:
            if not params:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, params)

    def close_connection(self):
        if self.connection:
            self.connection.close()

    # Method to check if the connection is closed
    def is_connection_closed(self):
        try:
            self.connection.execute("SELECT 1")
            return False
        except sqlite3.ProgrammingError:
            return True


class Clase(BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing
        self.__populate_table()  # If the table is already populated, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "clases" (
                "id" INTEGER,
                "clase" TEXT NOT NULL,
                PRIMARY KEY ("id")                               
            )
            """
        self.execute_query(sql)

    def __populate_table(self):
        # Check if the table already contains data
        sql = 'SELECT * FROM "clases"'
        self.execute_query(sql)
        is_populated = self.cursor.fetchone()

        # Only populate if the table is empty
        if not is_populated:
            for clase in const.ALLOWED_CLASES:
                self.__insert_data(clase)

    def __insert_data(self, clase):
        sql = 'INSERT INTO "clases" ("clase") VALUES (:clase)'
        params = {"clase": clase.lower()}
        self.execute_query(sql, params)

    def get_clase_id(self, clase):
        sql = 'SELECT * FROM "clases" WHERE "clase"=:clase'
        params = {"clase": clase.lower()}
        self.execute_query(sql, params)
        return self.cursor.fetchone()["id"]

    # def __delete_data(self): Won't have a method for deleting data because
    # it's a dimension table that stores static data (CONSTANTS)

    # def __update_data(self): Won't have a method for updating data because
    # it's a dimension table that stores static data (CONSTANTS)


class Uso(BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing
        self.__populate_table()  # If the table is already populated, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "usos" (
                "id" INTEGER,
                "uso_resumido" TEXT NOT NULL,
                "uso_completo" TEXT NOT NULL,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def __populate_table(self):
        sql = "SELECT * FROM usos"
        # Check if the table already contains data
        self.execute_query(sql)
        is_populated = self.cursor.fetchone()

        # Only populate if the table is empty
        if not is_populated:
            for uso_resumido, uso_completo in const.ALLOWED_USOS.items():
                self.__insert_data(uso_resumido, uso_completo)

    def __insert_data(self, uso_resumido, uso_completo):
        sql = 'INSERT INTO "usos" ("uso_resumido", "uso_completo") VALUES (:resumido, :completo)'
        params = {"resumido": uso_resumido.lower(), "completo": uso_completo.lower()}
        self.execute_query(sql, params)

    def get_uso_id(self, uso_resumido):
        sql = 'SELECT "id" FROM "usos" WHERE "uso_resumido"=:uso_resumido'
        params = {"uso_resumido": uso_resumido.lower()}
        self.execute_query(sql, params)
        return self.cursor.fetchone()["id"]

    # def __delete_data(self): Won't have a method for deleting data because
    # it's a dimension table that stores static data (CONSTANTS)

    # def __update_data(self): Won't have a method for updating data because
    # it's a dimension table that stores static data (CONSTANTS)


class AgrupacionCultivo(BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "agrupacion_cultivos" (
                "id" INTEGER,
                "agrupacion_cultivo" TEXT NOT NULL,
                PRIMARY KEY ("id")
            )        
"""
        self.execute_query(sql)

    def insert_data(self, agrupacion_cultivo):
        # If the argument is None, then do nothing
        if not agrupacion_cultivo:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_agrupacion_cultivo_id(agrupacion_cultivo):
            sql = 'INSERT INTO "agrupacion_cultivos" ("agrupacion_cultivo") VALUES (:agrupacion_cultivo)'
            params = {"agrupacion_cultivo": agrupacion_cultivo}
            self.execute_query(sql)

    def get_agrupacion_cultivo_id(self, agrupacion_cultivo):
        sql = 'SELECT id FROM "agrupacion_cultivos" WHERE "agrupacion_cultivo"=:agrupacion_cultivo'
        params = {"agrupacion_cultivo": agrupacion_cultivo}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table


class Aprovechamiento(BaseDatabase):  # Cultivo / aprovechamiento
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "aprovechamientos" (
                "id" INTEGER, 
                "aprovechamiento" TEXT NOT NULL,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def insert_data(self, aprovechamiento):
        # If the argument is None, then do nothing
        if not aprovechamiento:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_aprovechamiento_id(aprovechamiento):
            sql = 'INSERT INTO "aprovechamientos" ("aprovechamiento") VALUES (:aprovechamiento)'
            params = {"aprovechamiento": aprovechamiento}
            self.execute_query(sql, params)

    def get_aprovechamiento_id(self, aprovechamiento):
        sql = (
            'SELECT id FROM "aprovechamientos" WHERE "aprovechamiento"=:aprovechamiento'
        )
        params = {"aprovechamiento": aprovechamiento}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table


class Province(BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "provinces" (
                "id" INTEGER, 
                "province" TEXT NOT NULL,
                "rusticas_transactions_now" INTEGER,
                "rusticas_transactions_before" INTEGER,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def insert_data(
        self, province, rusticas_transactions_now, rusticas_transactions_before
    ):
        # If the argument is None, then do nothing
        if not province:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_province_id(province):
            sql = """
                    INSERT INTO "provinces" 
                    ("province","rusticas_transactions_now","rusticas_transactions_before")
                    VALUES (:province, :rusticas_transactions_now, :rusticas_transactions_before)
                """
            params = {
                "province": province,
                "rusticas_transactions_now": rusticas_transactions_now,
                "rusticas_transactions_before": rusticas_transactions_before,
            }
            self.execute_query(sql, params)

    def get_province_id(self, province):
        sql = """SELECT id FROM "provinces" WHERE "province"=:province"""
        params = {"province": province}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
    # (maybe for the transactions statistics) but they dont need to be updated till several years go by


class Municipio(BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "municipios" (
                "id" INTEGER, 
                "municipio" TEXT NOT NULL,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def insert_data(self, municipio):
        # If the argument is None, then do nothing
        if not municipio:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_municipio_id(municipio):
            sql = """
                    INSERT INTO "municipios" 
                    ("municipio")
                    VALUES (:municipio)
                """
            params = {
                "municipio": municipio,
            }
            self.execute_query(sql, params)

    def get_municipio_id(self, municipio):
        sql = """SELECT id FROM "municipios" WHERE "municipio"=:municipio"""
        params = {"municipio": municipio}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
    # (maybe for the transactions statistics) but they dont need to be updated till several years go by


class Locality(BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "localities" (
                "id" INTEGER,
                "locality" TEXT NOT NULL,
                "municipio_id" TEXT NOT NULL,
                "province_id" TEXT NOT NULL,
                "population_now" INTEGER,
                "population_before" INTEGER,
                PRIMARY KEY ("id"),
                FOREIGN KEY ("municipio_id") REFERENCES "municipios"("id"),
                FOREIGN KEY ("province_id") REFERENCES "provinces"("id")
            )
            """
        self.execute_query(sql)

    def insert_data(
        self, locality, municipio_id, province_id, population_now, population_before
    ):
        # If the argument is None, then do nothing
        if not locality:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_locality_id(locality, municipio_id):
            sql = """
                    INSERT INTO "localities" 
                    ("locality", "municipio_id", "province_id", "population_now", "population_before") 
                    VALUES (:locality, :municipio_id, :province_id, :population_now, :population_before)
                    """
            params = {
                "locality": locality,
                "municipio_id": municipio_id,
                "province_id": province_id,
                "population_now": population_now,
                "population_before": population_before,
            }
            self.execute_query(sql, params)

    def get_locality_id(self, locality, municipio_id):
        sql = 'SELECT "id" FROM "localities" WHERE "locality"=:locality AND "municipio_id"=:municipio_id'
        params = {"locality": locality, "municipio_id": municipio_id}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
    # (maybe for the population statistics) but they dont need to be updated till several years go by


class CodigoPostal(BaseDatabase):  # Código Postal
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "codigos_postales" (
                "id" INTEGER, 
                "codigo_postal" TEXT NOT NULL UNIQUE,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def insert_data(self, codigo_postal):
        # If the argument is None, then do nothing
        if not codigo_postal:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_codigo_postal_id(codigo_postal):
            sql = """
                    INSERT INTO "codigos_postales" 
                    ("codigo_postal")
                    VALUES (:codigo_postal)
                    """
            params = {"codigo_postal": codigo_postal}
            self.execute_query(sql, params)

    def get_codigo_postal_id(self, codigo_postal):
        sql = 'SELECT "id" FROM "codigos_postales" WHERE "codigo_postal"=:codigo_postal'
        params = {"codigo_postal": codigo_postal}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table


class Delegation(BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing
        self.__populate_table()  # If the table is already populated, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "delegations" (
                "id" INTEGER,
                "delegation" TEXT NOT NULL,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def __populate_table(self):
        # Check if the table already contains data
        sql = "SELECT * FROM delegations"
        self.execute_query(sql)
        is_populated = self.cursor.fetchone()

        # Only populate if the table is empty
        if not is_populated:
            for delegation in const.DELEGATIONS:
                delegation = const.DELEGATION_MAPPING[str(delegation)]
                self.__insert_data(delegation)

    def __insert_data(self, delegation):
        sql = 'INSERT INTO "delegations" ("delegation") VALUES (:delegation)'
        params = {"delegation": delegation}
        self.execute_query(sql, params)

    # def __delete_data(self): Won't have a method for deleting data because
    # it's a dimension table that stores static data (CONSTANTS)

    # def __update_data(self): Won't have a method for updating data because
    # it's a dimension table that stores static data (CONSTANTS)

    # def get_delegation_xxxx(self): Won't have a method for selecting data because
    # to insert data into the fincas table (delegation_id column),
    # I need to first retrieve the id from the delegations table,
    # but on this case I already have the id.


class Auction(BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "auctions" (
                "id" INTEGER,
                "electronical_id" TEXT UNIQUE,   
                "path_pdf" TEXT,
                "pliego_pdf" BLOB,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def insert_data(self, electronical_id, path_pdf):
        # If the argument is None, then do nothing
        if not electronical_id:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_auction_id(electronical_id):

            # Get the binary contents of the PDF to insert them on the BLOB field
            pliego_pdf = read_binary(path_pdf)

            sql = """
                    INSERT INTO "auctions"
                    ("electronical_id","path_pdf","pliego_pdf")
                    VALUES (:electronical_id,:path_pdf,:pliego_pdf)
                    """
            params = {
                "electronical_id": electronical_id,
                "path_pdf": path_pdf,
                "pliego_pdf": pliego_pdf,
            }
            self.execute_query(sql, params)

    def get_auction_id(self, electronical_id):
        sql = 'SELECT "id" FROM auctions WHERE "electronical_id"=:electronical_id'
        params = {"electronical_id": electronical_id}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table


class Territorio(BaseDatabase):  # ATH (agrupacion territorio homogeneo)
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "territorios" (
                "id" INTEGER,
                "ath_number" INTEGER NOT NULL,
                "ath_name" TEXT NOT NULL,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def insert_data(self, ath_number, ath_name):
        # If the argument is None, then do nothing
        if not ath_number:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_territorio_id(ath_number):
            sql = """
                    INSERT INTO "territorios" 
                    ("ath_number","ath_name")
                    VALUES (:ath_number, :ath_name)
                    """
            params = {"ath_number": ath_number, "ath_name": ath_name}
            self.execute_query(sql, params)

    def get_territorio_id(self, ath_number):
        sql = 'SELECT "id" FROM territorios WHERE "ath_number"=:ath_number'
        params = {"ath_number": ath_number}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table


class Lote(BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "lotes" (
                "id" INTEGER,
                "auction_id" INTEGER,
                "lote_number" INTEGER,
                "price" INTEGER,
                PRIMARY KEY ("id"),
                FOREIGN KEY ("auction_id") REFERENCES "auctions"("id")
            )
            """
        self.execute_query(sql)

    def insert_data(self, auction_id, lote_number, price):
        # If the argument is None, then do nothing
        if not auction_id:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_lote_id(auction_id, lote_number):
            sql = """
                    INSERT INTO "lotes" 
                    ("auction_id","lote_number","price")
                    VALUES (:auction_id, :lote_number, :price)
                    """
            params = {
                "auction_id": auction_id,
                "lote_number": lote_number,
                "price": price,
            }
            self.execute_query(sql, params)

    def get_lote_id(self, auction_id, lote_number):
        sql = 'SELECT "id" FROM lotes WHERE auction_id=:auction_id AND lote_number=:lote_number'
        params = {"auction_id": auction_id, "lote_number": lote_number}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table


class Empresa(BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "empresas" (
                "id" INTEGER, 
                {const.EMPRESAS_HEADERS}
                PRIMARY KEY ("id")
            )    
            """
        self.execute_query(sql)

    def insert_data(self, df):
        # If the argument is None, then do nothing
        if df is None:
            return None
        # Get the columns names to dynamically create the SQL statements
        list_columns_names = regex.findall(
            const.COLUMNS_PATTERN, const.EMPRESAS_HEADERS
        )
        list_columns_names = [column.strip() for column in list_columns_names]
        column_names_sql = ", ".join(list_columns_names)

        # Get the placeholders to dynamically create the SQL statements
        placeholders_sql = ", ".join(["?"] * len(list_columns_names))

        sql = f'INSERT INTO "empresas" ({column_names_sql}) VALUES ({placeholders_sql})'

        # The for loop iterates over the rows of the DataFrame using itertuples
        # (index=False, name=None), which returns each row as a tuple
        # without the index
        for row in df.itertuples(index=False, name=None):
            # Before inserting the data, check if already exists on the table
            # If it doesn't exists, then proceed to insert it
            if not self.get_empresa_id(row[1]):
                self.execute_query(sql, row)

    def get_empresa_id(self, nif):
        sql = 'SELECT "id" FROM empresas WHERE "Código NIF"=:nif'
        params = {"nif": nif}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    def delete_data(self, nif):
        sql = 'DELETE FROM empresas WHERE "Código NIF"=:nif'
        params = {"nif": nif}
        self.execute_query(sql, params)

    def testing_purposes(self):
        sql = 'SELECT "id" FROM empresas'
        result = self.execute_query(sql)
        return result["id"] if result else None

    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
    # the street and the financial ratios dont need to be updated till several years go by


class Finca(BaseDatabase):

    columns_sql = None
    placeholders_sql = None

    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing
        Finca.columns_sql, Finca.placeholders_sql = Finca.get_columns_placeholders_sql()

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "fincas" (
            "id" INTEGER, 
            {const.FINCA_HEADERS}
            PRIMARY KEY ("id"),
            FOREIGN KEY ("delegation_id") REFERENCES "delegations"("id"),
            FOREIGN KEY ("agrupacion_cultivo_id") REFERENCES "agrupacion_cultivos"("id"),
            FOREIGN KEY ("locality_id") REFERENCES "localities"("id"),
            FOREIGN KEY ("lote_id") REFERENCES "lotes"("id"),
            FOREIGN KEY ("clase_id") REFERENCES "clases"("id"),
            FOREIGN KEY ("uso_id") REFERENCES "usos"("id"),
            FOREIGN KEY ("aprovechamiento_id") REFERENCES "aprovechamientos"("id"),
            FOREIGN KEY ("codigo_postal_id") REFERENCES "codigos_postales"("id"),
            FOREIGN KEY ("ath_id") REFERENCES "territorios"("id")
            )
            """
        self.execute_query(sql)

    def insert_data(
        self, data, path_ortofoto, path_kml, path_google_maps, path_report_catastro
    ):
        # If the argument is None, then do nothing
        if not data:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_finca_id(data["referencia_catastral"]):

            # Get the binary contents of the ortofoto to insert them on the BLOB field
            ortofoto = read_binary(path_ortofoto)
            kml = read_binary(path_kml)
            google_maps = read_binary(path_google_maps)
            report_catastro = read_binary(path_report_catastro)

            sql = f'INSERT INTO "fincas" ({self.columns_sql}) VALUES ({self.placeholders_sql})'
            values = tuple(data.values())
            # Add the binary data to the end of the values tuple
            values += (ortofoto, kml, google_maps, report_catastro)

            self.execute_query(sql, values)

    def get_finca_id(self, ref):
        sql = 'SELECT "id" FROM fincas WHERE "referencia_catastral"=:ref'
        params = {"ref": ref}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table

    @staticmethod
    def get_columns_placeholders_sql():
        # Get the columns names to dynamically create the SQL statements
        # Drop last element, because the datetime would be inserted
        # by default, no need for a placeholder on sql statement
        list_columns_names = regex.findall(const.COLUMNS_PATTERN, const.FINCA_HEADERS)[
            :-1
        ]
        list_columns_names = [column.strip() for column in list_columns_names]
        column_names_sql = ", ".join(list_columns_names)
        # Get the placeholders to dynamically create the SQL statements
        placeholders_sql = ", ".join(["?"] * len(list_columns_names))
        return column_names_sql, placeholders_sql


class EmpresaFinca(BaseDatabase):

    # Class attributes
    columns_sql = None
    placeholders_sql = None

    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing
        EmpresaFinca.columns_sql, EmpresaFinca.placeholders_sql = (
            EmpresaFinca.get_columns_placeholders_sql()
        )

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "empresas_fincas" (
                "id" INTEGER,
                {const.EMPRESAS_FINCAS_HEADERS}
                PRIMARY KEY ("id"),
                FOREIGN KEY ("empresa_id") REFERENCES "empresas"("id") ON DELETE CASCADE,
                FOREIGN KEY ("finca_id") REFERENCES "fincas"("id")
            )
            """
        self.execute_query(sql)

    def insert_data(self, data):
        # If the argument is None, then do nothing
        if not data["empresa_id"]:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_empresa_finca_id(data["empresa_id"], data["finca_id"]):
            sql = f'INSERT INTO "empresas_fincas" ({self.columns_sql}) VALUES ({self.placeholders_sql})'
            values = tuple(data.values())
            self.execute_query(sql, values)

    def get_empresa_finca_id(self, empresa_id, finca_id):
        sql = 'SELECT "id" FROM empresas_fincas WHERE empresa_id=:empresa_id AND finca_id=:finca_id'
        params = {"empresa_id": empresa_id, "finca_id": finca_id}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def delete_data(self): Won't have a method for deleting data because it has no sense for this joint table
    # def update_data(self): Won't have a method for updating data because it has no sense for this dimension table

    @staticmethod
    def get_columns_placeholders_sql():
        # Get the columns names to dynamically create the SQL statements
        list_columns_names = regex.findall(
            const.COLUMNS_PATTERN, const.EMPRESAS_FINCAS_HEADERS
        )
        list_columns_names = [column.strip() for column in list_columns_names]
        column_names_sql = ", ".join(list_columns_names)
        # Get the placeholders to dynamically create the SQL statements
        placeholders_sql = ", ".join(["?"] * len(list_columns_names))
        return column_names_sql, placeholders_sql


# Returns Truthy value if its old, Falsy value if its new
def is_old(referencia_catastral):
    db = BaseDatabase()
    finca = Finca()
    finca_id = finca.get_finca_id(referencia_catastral)
    db.close_connection()
    return finca_id


def insert_land_data(land_data):

    # Create table if doesnt exist
    db = BaseDatabase()
    clase = Clase()
    uso = Uso()
    agrupacion_cultivo = AgrupacionCultivo()
    aprovechamiento = Aprovechamiento()
    province = Province()
    municipio = Municipio()
    locality = Locality()
    codigo_postal = CodigoPostal()
    delegation = Delegation()
    auction = Auction()
    territorio = Territorio()
    lote = Lote()
    empresa = Empresa()
    finca = Finca()

    empresa_finca = EmpresaFinca()

    #### 1) Insert data into dimension tables if it doesn't already exists

    ###  On the insert methods of each table (class) two things are already handled
    ###     a) Check if the data to be inserted != None.
    ###     b) Check if the data to be inserted is already on the table (then do nothing)

    # 1.1. Table 'clases' is already created and populated.
    # 1.2. Table 'usos' is already created and populated.
    # 1.3. Table 'agrupacion_cultivos'
    agrupacion_cultivo.insert_data(land_data["agrupacion_cultivo"])
    # 1.4. Table 'aprovechamientos'
    aprovechamiento.insert_data(land_data["aprovechamiento"])
    # 1.5. Table 'provinces'
    province.insert_data(
        land_data["province"],
        land_data["rusticas_transactions_now"],
        land_data["rusticas_transactions_before"],
    )
    # 1.6. Table 'municipios'
    municipio.insert_data(land_data["municipio"])
    # 1.7. Table 'localities'
    """Before inserting the data on 'localities' table, 
    I've to retrieve the id of the 'municipio' and 'province'
    that I inserted previously (they may've already exists
    on their tables, so it weren't inserted again)"""

    municipio_id = municipio.get_municipio_id(land_data["municipio"])
    province_id = province.get_province_id(land_data["province"])

    locality.insert_data(
        land_data["locality"],
        municipio_id,
        province_id,
        land_data["population_now"],
        land_data["population_before"],
    )
    # 1.7. Table 'codigos_postales'
    codigo_postal.insert_data(land_data["codigo_postal"])
    # 1.8. Table 'delegations' is already created and populated.
    # 1.9. Table 'auctions'
    auction.insert_data(land_data["electronical_id"], land_data["auction_pdf_path"])
    # 2.0. Table 'territorios'
    territorio.insert_data(land_data["ath_number"], land_data["ath_name"])
    # 2.1. Table 'lote'
    """Before inserting the data on 'lote' table, 
    I've to retrieve the id of the 'auction'
    that I inserted previously (they may've already exists
    on their tables, so it weren't inserted again)"""
    auction_id = auction.get_auction_id(land_data["electronical_id"])
    lote.insert_data(
        auction_id,
        land_data["lote_number"],
        land_data["price"],
    )
    # 2.2. Table 'empresa'
    empresa.insert_data(land_data["empresas"])
    # 2.3. Table 'finca'
    """Before inserting the data on 'finca' table, 
    I've to retrieve the id of the next variables:
        1. agrupacion_cultivo_id
        2. locality_id
        3. lote_id
        4. clase_id
        5. uso_id
        6. aprovechamiento_id
        7. codigo_postal_id
        8. ath_id
    that I inserted previously (they may've already exists
    on their tables, so it weren't inserted again)"""

    # Getting the necessaries IDs of the foreign keys
    agrupacion_cultivo_id = agrupacion_cultivo.get_agrupacion_cultivo_id(
        land_data["agrupacion_cultivo"]
    )
    locality_id = locality.get_locality_id(land_data["locality"], municipio_id)
    lote_id = lote.get_lote_id(auction_id, land_data["lote_number"])
    clase_id = clase.get_clase_id(land_data["clase"])
    uso_id = uso.get_uso_id(land_data["uso"])
    aprovechamiento_id = aprovechamiento.get_aprovechamiento_id(
        land_data["aprovechamiento"]
    )
    codigo_postal_id = codigo_postal.get_codigo_postal_id(land_data["codigo_postal"])
    ath_id = territorio.get_territorio_id(land_data["ath_number"])

    finca.insert_data(
        {
            "referencia_catastral": land_data["referencia_catastral"],
            "localizacion": land_data["localizacion"],
            "catastro_value": land_data["catastro_value"],
            "delegation_id": land_data["delegation"],
            "agrupacion_cultivo_id": agrupacion_cultivo_id,
            "locality_id": locality_id,
            "lote_id": lote_id,
            "clase_id": clase_id,
            "uso_id": uso_id,
            "aprovechamiento_id": aprovechamiento_id,
            "codigo_postal_id": codigo_postal_id,
            "ath_id": ath_id,
            "coordenadas": land_data["coordenadas"],
            "agrupacion_municipio": land_data["agrupacion_municipio"],
            "number_buildings": land_data["number_buildings"],
            "slope": land_data["slope"],
            "fls": land_data["fls"],
        },
        land_data["path_ortofoto_land"],
        land_data["path_kml_land"],
        land_data["path_googlemaps_land"],
        land_data["path_report_land"],
    )

    # 2.4. Table 'EmpresaFinca'
    """Before inserting the data on 'EmpresaFinca' table, 
    I've to retrieve the id of the next variables:
        1. finca_id      
        2. empresa_id
    that I inserted previously (they may've already exists
    on their tables, so it weren't inserted again)"""

    finca_id = finca.get_finca_id(land_data["referencia_catastral"])

    for empresa_finca_maps in land_data["empresas_fincas"]:

        empresa_finca_cif = empresa_finca_maps["cif"]
        empresa_finca_data = empresa_finca_maps["data"]

        # Get ID of enterprise
        empresa_id = empresa.get_empresa_id(empresa_finca_cif)

        # Get relevant data
        distance_on_car = empresa_finca_data["car"]["distance_on_car"]
        time_on_car = empresa_finca_data["car"]["time_on_car"]
        distance_on_foot = empresa_finca_data["foot"]["distance_on_foot"]
        time_on_foot = empresa_finca_data["foot"]["time_on_foot"]

        # Read binary file to insert on BLOB field in table
        path_route = empresa_finca_data["path"]
        binary_content = read_binary(path_route)

        data_to_insert = {
            "empresa_id": empresa_id,
            "finca_id": finca_id,
            "distance_on_car": distance_on_car,
            "time_on_car": time_on_car,
            "distance_on_foot": distance_on_foot,
            "time_on_foot": time_on_foot,
            "route_screenshot": binary_content,
        }
        empresa_finca.insert_data(data_to_insert)

    remove_file_from_filesystem(land_data["auction_pdf_path"])
    remove_file_from_filesystem(land_data["path_ortofoto_land"])
    remove_file_from_filesystem(land_data["path_kml_land"])
    remove_file_from_filesystem(land_data["path_googlemaps_land"])
    remove_file_from_filesystem(land_data["path_report_land"])
    remove_file_from_filesystem(empresa_finca_data["path"])

    db.close_connection()
