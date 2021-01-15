import atexit
import sqlite3
from dto import *


# Data Access Objects:
# All of these are meant to be singletons
class _Vaccines:
    def __init__(self, conn):
        self._conn = conn

    def insert(self, vaccine):
        self._conn.execute("""
               INSERT INTO vaccines (date, supplier, quantity) VALUES (?, ?, ?)
           """, [vaccine.date, vaccine.supplier, vaccine.quantity])

    def find(self, vaccine_id):
        c = self._conn.cursor()
        c.execute("""
            SELECT id, date, supplier, quantity FROM vaccines WHERE id = ?
        """, [vaccine_id])

        return Vaccine(*c.fetchone())

    def take(self, vaccine_id, amount):
        c = self._conn.cursor()
        c.execute("""
            SELECT quantity FROM vaccines WHERE id = ?
        """, [vaccine_id])
        curr_quantity = int(*c.fetchone())
        amount = min(curr_quantity, amount)
        if curr_quantity>amount:
            self._conn.execute("""
                    UPDATE vaccines 
                    SET quantity = quantity - ?
                    WHERE id = ?
               """, [amount, vaccine_id])
        else:
            self._conn.execute("""
                    DELETE FROM vaccines 
                    WHERE id = ?
               """, [amount, vaccine_id])

        return amount


class _Suppliers:
    def __init__(self, conn):
        self._conn = conn

    def insert(self, supplier):
        self._conn.execute("""
                INSERT INTO suppliers (id, name, logistic) VALUES (?, ?, ?)
        """, [supplier.id, supplier.name, supplier.logistic])

    def find(self, supplier_id):
        c = self._conn.cursor()
        c.execute("""
                SELECT id, name, logistic FROM suppliers WHERE id = ?
            """, [supplier_id])

        return Supplier(*c.fetchone())


class _Clinics:
    def __init__(self, conn):
        self._conn = conn

    def insert(self, clinic):
        self._conn.execute("""
            INSERT INTO clinics (id, location, demand, logistic) VALUES (?, ?, ?, ?)
        """, [clinic.id, clinic.location, clinic.demand, clinic.logistic])

    def find(self, clinic_id):
        c = self._conn.cursor()
        c.execute("""
                SELECT id, location, demand, logistic FROM clinics WHERE id = ?
            """, [clinic_id])

        return Clinic(*c.fetchone())

    def lower_demand(self, location, amount):
        self._conn.execute("""
                UPDATE clinics 
                SET demand = demand - ?
                WHERE location = ?
           """, [amount, location])


class _Logistics:
    def __init__(self, conn):
        self._conn = conn

    def insert(self, logistic):
        self._conn.execute("""
            INSERT INTO logistics (id, name, count_sent, count_received) VALUES (?, ?, ?, ?)
        """, [logistic.id, logistic.name, logistic.count_sent, logistic.count_received])

    def find(self, logistic_id):
        c = self._conn.cursor()
        c.execute("""
                SELECT id, name, count_sent, count_received FROM logistics WHERE id = ?
            """, [logistic_id])

        return Logistic(*c.fetchone())

    def increase_count_received(self, name, amount):
        self._conn.execute("""
                UPDATE logistics 
                SET count_received = count_received + (?)
                WHERE name = (?)
           """, [amount, name])

    def increase_count_send(self, name, amount):
        self._conn.execute("""
                UPDATE logistics 
                SET count_sent = count_sent + (?)
                WHERE name = (?)
           """, [amount, name])


# The Repository
class _Repository:
    def __init__(self):
        self._conn = sqlite3.connect('database.db')
        self.vaccines = _Vaccines(self._conn)
        self.suppliers = _Suppliers(self._conn)
        self.clinics = _Clinics(self._conn)
        self.logistics = _Logistics(self._conn)

    def _close(self):
        self._conn.commit()
        self._conn.close()

    def create_tables(self):
        self._conn.executescript("""
        CREATE TABLE vaccines (
            id         INT         PRIMARY KEY,
            date       DATE        NOT NULL,
            supplier   INT,
            quantity   INT         NOT NULL,
            
            FOREIGN KEY(supplier)     REFERENCES suppliers(id)
        );

        CREATE TABLE suppliers (
            id            INT     PRIMARY KEY,
            name          TEXT    NOT NULL,
            logistic      INT,
            
            FOREIGN KEY(logistic)     REFERENCES logistics(id)
        );

        CREATE TABLE clinics (
            id         INT     PRIMARY KEY,
            location   TEXT    NOT NULL,
            demand     INT     NOT NULL,
            logistic   INT,

            FOREIGN KEY(logistic)     REFERENCES logistics(id)
        );
        
        CREATE TABLE logistics (
            id                 INT     PRIMARY KEY,
            name               TEXT    NOT NULL,
            count_sent         INT     NOT NULL,
            count_received     INT     NOT NULL
        );

    """)


# the repository singleton
repo = _Repository()
atexit.register(repo._close)
