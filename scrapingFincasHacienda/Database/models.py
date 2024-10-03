import sqlite3
import Database.constants as const
import regex


def to_str(list):
    return ", ".join(f"'{item}'" for item in list)


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
        params = {"clase": clase}
        self.execute_query(sql, params)

    def get_clase_id(self, clase):
        sql = 'SELECT * FROM "clases" WHERE "clase"=:clase'
        params = {"clase": clase}
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
        params = {"resumido": uso_resumido, "completo": uso_completo}
        self.execute_query(sql, params)

    def get_uso_id(self, uso_resumido):
        sql = 'SELECT "id" FROM "usos" WHERE "uso_resumido"=:uso_resumido'
        params = {"uso_resumido": uso_resumido}
        self.execute_query(sql, params)
        return self.cursor.fetchone()["id"]

    # def __delete_data(self): Won't have a method for deleting data because
    # it's a dimension table that stores static data (CONSTANTS)

    # def __update_data(self): Won't have a method for updating data because
    # it's a dimension table that stores static data (CONSTANTS)


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
        sql = 'INSERT INTO "aprovechamientos" ("aprovechamiento") VALUES (:aprovechamiento)'
        params = {"aprovechamiento": aprovechamiento}
        self.execute_query(sql, params)

    def get_aprovechamiento_id(self, aprovechamiento):
        sql = (
            'SELECT id FROM "aprovechamientos" WHERE "aprovechamiento"=:aprovechamiento'
        )
        params = {"aprovechamiento": aprovechamiento}
        self.execute_query(sql, params)
        return self.cursor.fetchone()["id"]

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table


class Locality(BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "localities" (
                "id" INTEGER,
                "locality" TEXT NOT NULL,
                "municipio" TEXT NOT NULL,
                "population_now" INTEGER,
                "population_before" INTEGER,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def insert_data(self, locality, municipio, population_now, population_before):
        sql = """
                INSERT INTO "localities" 
                ("locality", "municipio", "population_now", "population_before") 
                VALUES (:locality, :municipio, :population_now, :population_before)
                """
        params = {
            "locality": locality,
            "municipio": municipio,
            "population_now": population_now,
            "population_before": population_before,
        }
        self.execute_query(sql, params)

    def get_locality_id(self, locality, municipio):
        sql = 'SELECT "id" FROM "localities" WHERE "locality"=:locality AND "municipio"=:municipio'
        params = {"locality": locality, "municipio": municipio}
        self.execute_query(sql, params)
        return self.cursor.fetchone()["id"]

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
    # (maybe for the population statistics) but they dont need to be updated till several years go by


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
        return self.cursor.fetchone()["id"]

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
    # (maybe for the transactions statistics) but they dont need to be updated till several years go by


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
        return self.cursor.fetchone()["id"]

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
                "auction_url" TEXT UNIQUE NOT NULL,
                "pliego_pdf" BLOB,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def insert_data(self, auction_url, file_path):
        with open(file_path, "rb") as file:
            file_content = file.read()
        sql = """
                INSERT INTO "auctions"
                ("auction_url", "pliego_pdf")
                VALUES (:auction_url, :pliego_pdf)
                """
        params = {"auction_url": auction_url, "pliego_pdf": file_content}
        self.execute_query(sql, params)

    def get_auction_id(self, auction_url):
        sql = 'SELECT "id" FROM auctions WHERE "auction_url"=:auction_url'
        params = {"auction_url": auction_url}
        self.execute_query(sql, params)
        return self.cursor.fetchone()["id"]

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
        return self.cursor.fetchone()["id"]

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
        sql = """
                INSERT INTO "lotes" 
                ("auction_id","lote_number","price")
                VALUES (:auction_id, :lote_number, :price)
                """
        params = {"auction_id": auction_id, "lote_number": lote_number, "price": price}
        self.execute_query(sql, params)

    def get_lote_id(self, auction_id, lote_number):
        sql = 'SELECT "id" FROM lotes WHERE auction_id=:auction_id AND lote_number=:lote_number'
        params = {"auction_id": auction_id, "lote_number": lote_number}
        self.execute_query(sql, params)
        return self.cursor.fetchone()["id"]

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
            self.execute_query(sql, row)

    def get_empresa_id(self, nif):
        sql = 'SELECT "id" FROM empresas WHERE "Código NIF"=:nif'
        params = {"nif": nif}
        self.execute_query(sql, params)
        return self.cursor.fetchone()["id"]

    def delete_data(self, nif):
        sql = 'DELETE FROM empresas WHERE "Código NIF"=:nif'
        params = {"nif": nif}
        self.execute_query(sql, params)

    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
    # the street and the financial ratios dont need to be updated till several years go by


class Finca(BaseDatabase):

    columns_sql = None
    placeholders_sql = None

    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing
        Finca.columns, Finca.placeholders_sql = Finca.get_columns_placeholders_sql()

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "fincas" (
            "id" INTEGER, 
            {const.FINCA_HEADERS}
            PRIMARY KEY ("id"),
            FOREIGN KEY ("lote_id") REFERENCES "lotes"("id"),
            FOREIGN KEY ("clase_id") REFERENCES "clases"("id"),
            FOREIGN KEY ("uso_id") REFERENCES "usos"("id"),
            FOREIGN KEY ("aprovechamiento_id") REFERENCES "aprovechamientos"("id"),
            FOREIGN KEY ("codigo_postal_id") REFERENCES "codigos_postales"("id"),
            FOREIGN KEY ("ath_id") REFERENCES "territorios"("id")
            )
            """
        self.execute_query(sql)

    def insert_data(self, data):
        sql = f'INSERT INTO "empresas" ({self.columns_sql}) VALUES ({self.placeholders_sql})'
        values = tuple(data.values())
        self.execute_query(sql, values)

    def get_finca_id(self, ref):
        sql = 'SELECT "id" FROM fincas WHERE "referencia_catastral"=:ref'
        params = {"ref": ref}
        self.execute_query(sql, params)
        return self.cursor.fetchone()["id"]

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table

    @staticmethod
    def get_columns_placeholders_sql():
        # Get the columns names to dynamically create the SQL statements
        list_columns_names = regex.findall(const.COLUMNS_PATTERN, const.FINCA_HEADERS)
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
        EmpresaFinca.columns, EmpresaFinca.placeholders_sql = (
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
        sql = f'INSERT INTO "empresas" ({self.columns_sql}) VALUES ({self.placeholders_sql})'
        values = tuple(data.values())
        self.execute_query(sql, values)

    # def get_Empresa_Finca_id(self): Won't have a method to retrive the ID because it's not used a foreign key in any other table
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
