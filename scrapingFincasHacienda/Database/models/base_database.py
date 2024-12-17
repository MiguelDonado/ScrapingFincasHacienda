import sqlite3
from pathlib import Path

import Database.constants as const
import regex


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

    #####
    ########
    ############# HELPER FUNCTIONS (USED BY THE CHILD CLASSES)
    ########
    #####

    @staticmethod
    def read_binary(path_binary_file):
        # If the path to the binary file is empty.
        # i.e. when a land doesnt have the report from the catastro
        # the path_report_catastro'll be None
        if not path_binary_file:
            return None
        with open(path_binary_file, "rb") as file:
            binary_file = file.read()
        return binary_file

    @staticmethod
    def remove_file_from_filesystem(path):
        if path:
            file_path = Path(path)
            try:
                file_path.unlink()
            except Exception:
                return None
        else:
            return None

    @staticmethod
    def get_columns_and_placeholders_sql():
        # 1) In some classes ("Finca","EmpresaFinca") I create two class attributes.
        # 2) This class attributtes are called "columns_sql" and "placeholders_sql".
        # 3) "columns_sql": Will hold the values for
        # 4)
        # sql = f'INSERT INTO "fincas" ({self.columns_sql}) VALUES ({self.placeholders_sql})'
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

        # Get the columns names to dynamically create the SQL statements
        list_columns_names = regex.findall(
            const.COLUMNS_PATTERN, const.EMPRESAS_FINCAS_HEADERS
        )
        list_columns_names = [column.strip() for column in list_columns_names]
        column_names_sql = ", ".join(list_columns_names)
        # Get the placeholders to dynamically create the SQL statements
        placeholders_sql = ", ".join(["?"] * len(list_columns_names))
        return column_names_sql, placeholders_sql

    @staticmethod
    def is_len_placeholders_equals_len_values(placeholders, values):
        pass
        # # Ensure the number of placeholders matches the number of values
        # assert len(self.placeholders_sql.split(",")) == len(
        #     values
        # ), f"Expected {len(self.placeholders_sql.split(','))} values, but got {len(values)}.\nPlaceholders: {self.placeholders_sql.split(',')}\n\nValues: {values}"
