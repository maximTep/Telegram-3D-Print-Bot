import sqlite3
import subprocess




class DataBase:
    def __init__(self):
        self.conn = sqlite3.connect('DataBase\\DataBase3D.db', check_same_thread=False)
        self.curs = self.conn.cursor()
        self.curs.execute("""
                        CREATE TABLE IF NOT EXISTS orders(
                        order_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        service TEXT NOT NULL,
                        has_model TEXT NOT NULL DEFAULT 'Нет',
                        eval_price INTEGER NOT NULL DEFAULT '-1',
                        has_blueprint TEXT NOT NULL DEFAULT 'Нет',
                        has_photo TEXT NOT NULL DEFAULT 'Нет',
                        description TEXT NOT NULL DEFAULT 'Нет',
                        material TEXT NOT NULL DEFAULT 'Консультация инженера',
                        wishes TEXT NOT NULL DEFAULT 'Нет',
                        contacts TEXT NOT NULL DEFAULT 'Нет'
                        );
                        """)
        self.conn.commit()

    def get_new_id(self):
        self.curs.execute('SELECT MAX(order_id) FROM orders;')
        self.conn.commit()
        new_id = self.curs.fetchone()[0]
        if new_id is None:
            new_id = 1253
        return new_id

    def update_visual_orders_file(self):
        subprocess.call(["SQLite3\\sqlite3.exe", 'DataBase\\DataBase3D.db',
                         ".mode csv",
                         ".headers on",
                         ".cd DataBase",
                         '.output  orders.csv',
                         "SELECT * FROM orders;"])

    def add_order(self, order: dict):
        req = 'INSERT INTO orders('
        for ind, key in enumerate(order.keys()):
            if ind == len(order.keys())-1:
                req += f'{key}) '
            else:
                req += f'{key}, '
        req += 'VALUES('
        for ind, val in enumerate(order.values()):
            if ind == len(order.values())-1:
                req += f"'{val}');"
            else:
                req += f"'{val}', "
        self.curs.execute(req)
        self.conn.commit()
        self.update_visual_orders_file()












