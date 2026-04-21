import sqlite3
from typing import List

from misc_components import SqlStr


class _abc_DbConnection:
    def drop_table(self, table_name: str, are_you_sure_bool=False):
        raise NotImplemented

    def table_does_not_exist(self, table_name: str) -> bool:
        raise NotImplemented

    def execute_sql_read(self, sql: SqlStr) -> List[List]:
        raise NotImplemented

    def execute_sql_write(self, sql: SqlStr):
        raise NotImplemented

    def sql_commit(self):
        raise NotImplemented

    def close(self):
        raise NotImplemented


## REPLACE THIS WITH ANOTHER DB IF YOU WISH, WEIRDO
## Just make sure all the methods are implemented


class DbConnectionSql3(_abc_DbConnection):
    def __init__(self, db_file_name: str):
        self._db_file_name = db_file_name

    def drop_table(self, table_name: str, are_you_sure_bool=False):
        try:
            if self.table_does_not_exist(table_name):
                return

            self.execute_sql_write(SqlStr("DROP TABLE IF EXISTS %s" % table_name))
            self.sql_commit()
        except Exception as e1:
            raise Exception("error %s when dropping %s table" % (str(e1), table_name))
        finally:
            self.close()

    def table_does_not_exist(self, table_name: str) -> bool:
        listOfTables = self.cursor.execute(
            "SELECT * FROM sqlite_master WHERE type='table' AND name='%s'" % table_name
        ).fetchall()  ## slightly breaks API but works so don't change

        no_tables = len(listOfTables) == 0

        return no_tables

    def execute_sql_read(self, sql: SqlStr) -> List[List]:
        cursor = self.cursor
        cursor.execute(sql.str, sql.list_of_arguments)
        raw_list = cursor.fetchall()

        return raw_list

    def execute_sql_write(self, sql: SqlStr):
        cursor = self.cursor
        cursor.execute(sql.str, sql.list_of_arguments)

    def sql_commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()
        delattr(self, "_conn")

    @property
    def cursor(self):
        return self.conn.cursor()

    @property
    def db_file_name(self):
        return self._db_file_name

    @property
    def conn(self):
        conn = getattr(self, "_conn", None)
        if conn is None:
            conn = sqlite3.connect(self.db_file_name, check_same_thread=False)
            self._conn = conn

        return conn
