import sqlite3
import Database.constants as const


def to_str(list):
    return ", ".join(f"'{item}'" for item in list)


class Clase:
    def __init__(self, db_name=const.DB_NAME):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row  # Enable named tuple access
        self.cursor = self.connection.cursor()
        self.__create_table()
        self.__populate_table()

    def __create_table(self):
        with self.connection:
            self.cursor.execute(
                f"""
            CREATE TABLE IF NOT EXISTS clases (
                id INTEGER,
                clase TEXT NOT NULL,
                PRIMARY KEY ("id")                               
            )
            """
            )

    def __populate_table(self):
        with self.connection:
            # Check if the table already contains data
            self.cursor.execute("SELECT * FROM clases")
            is_populated = self.cursor.fetchone()

            # Only populate if the table is empty
            if not is_populated:
                for clase in const.ALLOWED_CLASES:
                    self.__insert_data(clase)

    def __insert_data(self, clase):
        self.cursor.execute(
            'INSERT INTO clases ("clase") VALUES (:clase)',
            {"clase": clase},
        )


class Uso:
    def __init__(self, db_name=const.DB_NAME):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row  # Enable named tuple access
        self.cursor = self.connection.cursor()
        self.__create_table()
        self.__populate_table()

    def __create_table(self):
        with self.connection:
            self.cursor.execute(
                f"""
            CREATE TABLE IF NOT EXISTS usos (
                id INTEGER,
                uso_resumido TEXT NOT NULL,
                uso_completo TEXT NOT NULL,
                PRIMARY KEY ("id")
            )
            """
            )

    def __populate_table(self):
        with self.connection:
            # Check if the table already contains data
            self.cursor.execute("SELECT * FROM usos")
            is_populated = self.cursor.fetchone()

            # Only populate if the table is empty
            if not is_populated:
                for uso_resumido, uso_completo in const.ALLOWED_USOS.items():
                    self.__insert_data(uso_resumido, uso_completo)

    def __insert_data(self, uso_resumido, uso_completo):
        self.cursor.execute(
            'INSERT INTO usos ("uso_resumido", "uso_completo") VALUES (:resumido, :completo)',
            {"resumido": uso_resumido, "completo": uso_completo},
        )

    # def __delete_data(self): Won't have a method for deleting data because
    # it's a dimension table that stores static data (CONSTANTS)

    # def __update_data(self): Won't have a method for updating data because
    # it's a dimension table that stores static data (CONSTANTS)

    def get_uso_id(self, uso_resumido):
        with self.connection:
            self.cursor.execute(
                "SELECT id FROM usos WHERE uso_resumido=:uso_resumido",
                {"uso_resumido": uso_resumido},
            )
            return self.cursor.fetchone()["id"]


class Aprovechamiento:  # Cultivo / aprovechamiento
    def __init__(self, db_name=const.DB_NAME):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row  # Enable named tuple access
        self.cursor = self.connection.cursor()
        self.__create_table()

    def __create_table(self):
        with self.connection:
            self.cursor.execute(
                f"""
            CREATE TABLE IF NOT EXISTS aprovechamientos (
                id INTEGER, 
                aprovechamiento TEXT NOT NULL,
                PRIMARY KEY ("id")
            )
            """
            )


class CodigoPostal:  # Código Postal
    def __init__(self, db_name=const.DB_NAME):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row  # Enable named tuple access
        self.cursor = self.connection
        self.__create_table()

    def __create_table(self):
        with self.connection:
            self.cursor.execute(
                f"""
            CREATE TABLE IF NOT EXISTS codigos_postales (
                id INTEGER, 
                codigo_postal TEXT NOT NULL UNIQUE,
                locality_id INTEGER,
                province_id INTEGER,
                PRIMARY KEY ("id"),
                FOREIGN KEY ("locality_id") REFERENCES "localities"("id")
                FOREIGN KEY ("province_id") REFERENCES "provinces"("id")
            )
            """
            )


class Locality:
    def __init__(self, db_name=const.DB_NAME):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row  # Enable named tuple access
        self.cursor = self.connection.cursor()
        self.__create_table()

    def __create_table(self):
        with self.connection:
            self.cursor.execute(
                f"""
            CREATE TABLE IF NOT EXISTS localities (
                id INTEGER,
                locality TEXT NOT NULL,
                municipio TEXT NOT NULL,
                population_now INTEGER,
                population_before INTEGER,
                population_variation NUMERIC,
                PRIMARY KEY ("id")
            )
            """
            )


class Province:
    def __init__(self, db_name=const.DB_NAME):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row  # Enable named tuple access
        self.cursor = self.connection.cursor()
        self.__create_table()

    def __create_table(self):
        with self.connection:
            self.cursor.execute(
                f"""
            CREATE TABLE IF NOT EXISTS provinces (
                id INTEGER, 
                province TEXT NOT NULL,
                rusticas_transactions_now INTEGER,
                rusticas_transactions_before INTEGER,
                rusticas_transactions_variation NUMERIC,
                PRIMARY KEY ("id")
            )
            """
            )


class Empresa:
    def __init__(self, db_name=const.DB_NAME):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row  # Enable named tuple access
        self.cursor = self.connection.cursor()
        self.__create_table()

    def __create_table(self):
        with self.connection:
            self.cursor.execute(
                f"""
            CREATE TABLE IF NOT EXISTS empresas (
                id INTEGER, 
                {const.EMPRESAS_HEADERS}
                PRIMARY KEY ("id")
            )    
            """
            )


class Delegation:
    def __init__(self, db_name=const.DB_NAME):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row  # Enable named tuple access
        self.cursor = self.connection.cursor()
        self.__create_table()
        self.__populate_table()

    def __create_table(self):
        with self.connection:
            self.cursor.execute(
                f"""
            CREATE TABLE IF NOT EXISTS delegations (
                id INTEGER,
                delegation TEXT NOT NULL,
                PRIMARY KEY ("id")
            )
            """
            )

    def __populate_table(self):
        with self.connection:
            # Check if the table already contains data
            self.cursor.execute("SELECT * FROM delegations")
            is_populated = self.cursor.fetchone()

            # Only populate if the table is empty
            if not is_populated:
                for delegation in const.DELEGATIONS:
                    delegation = const.DELEGATION_MAPPING[str(delegation)]
                    self.__insert_data(delegation)

    def __insert_data(self, delegation):
        self.cursor.execute(
            'INSERT INTO delegations ("delegation") VALUES (:delegation)',
            {"delegation": delegation},
        )

    # def __delete_data(self): Won't have a method for deleting data because
    # it's a dimension table that stores static data (CONSTANTS)

    # def __update_data(self): Won't have a method for updating data because
    # it's a dimension table that stores static data (CONSTANTS)

    # def __get_delegation_xxxx(self): Won't have a method for selecting data because
    # to insert data into the fincas table (delegation_id column),
    # I need to first retrieve the id from the delegations table,
    # but on this case I already have the id.


class Auction:
    def __init__(self, db_name=const.DB_NAME):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row  # Enable named tuple access
        self.cursor = self.connection.cursor()
        self.__create_table()

    def __create_table(self):
        with self.connection:
            self.cursor.execute(
                f"""
            CREATE TABLE IF NOT EXISTS auctions (
                id INTEGER,
                delegation_id INTEGER NOT NULL,
                auction_url TEXT UNIQUE NOT NULL,
                auction_pdf BLOB,
                PRIMARY KEY ("id"),
                FOREIGN KEY ("delegation_id") REFERENCES "delegations"("id")
            )
            """
            )


class Lote:
    def __init__(self, db_name=const.DB_NAME):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row  # Enable named tuple access
        self.cursor = self.connection.cursor()
        self.__create_table()

    def __create_table(self):
        with self.connection:
            self.cursor.execute(
                f"""
            CREATE TABLE IF NOT EXISTS lotes (
                id INTEGER,
                auction_id INTEGER NOT NULL,
                number_fincas INTEGER NOT NULL,
                price INTEGER,
                PRIMARY KEY ("id"),
                FOREIGN KEY ("auction_id") REFERENCES "auctions"("id")
            )

            """
            )


class Territorio:  # ATH (agrupacion territorio homogeneo)
    def __init__(self, db_name=const.DB_NAME):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row  # Enable named tuple access
        self.cursor = self.connection.cursor()
        self.__create_table()

    def __create_table(self):
        with self.connection:
            self.cursor.execute(
                f"""
            CREATE TABLE IF NOT EXISTS territorios (
                id INTEGER,
                ath_number INTEGER NOT NULL,
                ath_name TEXT NOT NULL,
                PRIMARY KEY ("id")
            )
            """
            )


class Finca:
    def __init__(self, db_name=const.DB_NAME):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row  # Enable named tuple access
        self.cursor = self.connection.cursor()
        self.__create_table()

    def __create_table(self):
        with self.connection:
            self.cursor.execute(
                f"""
            CREATE TABLE IF NOT EXISTS fincas (
            id INTEGER, 
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
            )


class EmpresaFinca:
    def __init__(self, db_name=const.DB_NAME):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row  # Enable named tuple access
        self.cursor = self.connection.cursor()
        self.__create_table()

    def __create_table(self):
        with self.connection:
            self.cursor.execute(
                f"""
            CREATE TABLE IF NOT EXISTS empresas_fincas (
                id INTEGER,
                empresa_id INTEGER NOT NULL,
                finca_id INTEGER NOT NULL,
                distance_on_car INTEGER NOT NULL,
                time_on_car INTEGER NOT NULL,
                distance_on_foot INTEGER NOT NULL,
                time_on_foot INTEGER NOT NULL,
                route_screenshot BLOB,
                PRIMARY KEY ("id"),
                FOREIGN KEY ("empresa_id") REFERENCES "empresas"("id"),
                FOREIGN KEY ("finca_id") REFERENCES "fincas"("id")
            )
            """
            )
