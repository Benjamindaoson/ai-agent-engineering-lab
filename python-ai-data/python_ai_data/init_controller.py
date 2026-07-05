import sqlite3

from .dto import ColumnInfo, TableInfo


class InitController:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def init(self) -> list[TableInfo]:
        tables = []
        for row in self.connection.execute("select name from sqlite_master where type='table' order by name"):
            table_name = row[0]
            columns = []
            for column in self.connection.execute(f"pragma table_info({table_name})"):
                columns.append(ColumnInfo(column[1], column[2], column[1]))
            tables.append(TableInfo(table_name, table_name, columns))
        return tables

    def search(self, question: str) -> list[TableInfo]:
        keywords = [part.lower() for part in question.split() if part.strip()]
        return [
            table
            for table in self.init()
            if any(keyword in table.table_name.lower() or any(keyword in col.column_name.lower() for col in table.column_info_list) for keyword in keywords)
        ]


def create_demo_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.execute("create table orders (order_id integer, total_amount real, status text)")
    connection.execute("insert into orders values (1, 100.0, 'paid')")
    connection.execute("insert into orders values (2, 50.0, 'pending')")
    connection.execute("create table products (product_id integer, product_name text, sales integer)")
    connection.execute("insert into products values (1, 'phone', 20)")
    connection.commit()
    return connection
