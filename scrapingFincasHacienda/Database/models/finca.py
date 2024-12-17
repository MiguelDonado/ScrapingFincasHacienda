import sqlite3
from pathlib import Path

import Database.constants as const
import Database.models.base_database as Db
import regex


class Finca(Db.BaseDatabase):

    columns_sql, placeholders_sql = Db.BaseDatabase.get_columns_and_placeholders_sql()

    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

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
            FOREIGN KEY ("ath_id") REFERENCES "territorios"("id"),
            FOREIGN KEY ("cubierta_terrestre_iberpix_id") REFERENCES "cubiertas_terrestres_iberpix"("id"),
            FOREIGN KEY ("cubierta_terrestre_codigee_id") REFERENCES "cubiertas_terrestres_codigee"("id"),
            FOREIGN KEY ("uso_suelo_hilucs_id") REFERENCES "usos_suelo_hilucs"("id")
            )
            """
        self.execute_query(sql)

    def insert_data(
        self,
        data,
        path_ortofoto,
        path_kml,
        path_google_maps,
        path_report_catastro,
        path_curvas_nivel,
        path_lidar,
        path_usos_suelo,
        path_ortofoto_hidrografia,
    ):
        # If the argument is None, then do nothing
        if not data:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_finca_id(data["referencia_catastral"]):

            # Get the binary contents of the ortofoto to insert them on the BLOB field
            ortofoto = Db.BaseDatabase.read_binary(path_ortofoto)
            kml = Db.BaseDatabase.read_binary(path_kml)
            google_maps = Db.BaseDatabase.read_binary(path_google_maps)
            curvas_nivel = Db.BaseDatabase.read_binary(path_curvas_nivel)
            lidar = Db.BaseDatabase.read_binary(path_lidar)
            usos_suelo = Db.BaseDatabase.read_binary(path_usos_suelo)
            hidrografia = Db.BaseDatabase.read_binary(path_ortofoto_hidrografia)
            report_catastro = Db.BaseDatabase.read_binary(path_report_catastro)

            sql = f'INSERT INTO "fincas" ({self.columns_sql}) VALUES ({self.placeholders_sql})'
            values = tuple(data.values())
            # Add the binary data to the end of the values tuple
            values += (
                ortofoto,
                kml,
                google_maps,
                curvas_nivel,
                lidar,
                usos_suelo,
                hidrografia,
                report_catastro,
            )

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
