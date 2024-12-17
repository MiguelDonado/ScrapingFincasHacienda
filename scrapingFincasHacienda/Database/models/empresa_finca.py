import sqlite3
from pathlib import Path

import Database.constants as const
import Database.models.base_database as Db
import regex


class EmpresaFinca(Db.BaseDatabase):

    # Class attributes
    columns_sql, placeholders_sql = Db.BaseDatabase.get_columns_placeholders_sql()

    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

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
