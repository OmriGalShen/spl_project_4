import atexit
import sqlite3
from dto import *


# Data Access Objects:
# All of these are meant to be singletons
class _Vaccines:
    def __init__(self, conn):
        self._conn = conn
        self.counter = 1

    def insert(self, vaccine):
        self._conn.execute("""
               INSERT INTO vaccines (id, date, supplier, quantity) VALUES (?, ?, ?, ?)
           """, [self.counter, vaccine.date, vaccine.supplier, vaccine.quantity])
        self.counter += 1

    def find(self, vaccine_id):
        c = self._conn.cursor()
        c.execute("""
            SELECT id, date, supplier, quantity FROM vaccines WHERE id = ?
        """, [vaccine_id])

        return Vaccine(*c.fetchone())

    def take(self, amount):
        suppliers = []
        c = self._conn.cursor()
        c.execute("""
            SELECT * FROM vaccines ORDER BY date
        """, )

        vaccines = [Vaccine(*entry) for entry in c.fetchall()]
        ind = 0
        left = amount
        while left > 0 and ind < len(vaccines):
            current = vaccines[ind]
            quantity = current.quantity
            if quantity <= left:
                self.delete(current.id)
                left -= quantity
            else:
                quantity -= left
                left = 0
                self.update_quantity(current.id, quantity)
            suppliers.append((current.supplier, quantity))
            ind += 1

        return amount-left, suppliers

    def total_inventory(self):
        c = self._conn.cursor()
        c.execute("""
            SELECT SUM(quantity) FROM vaccines
        """)
        temp = c.fetchone()
        if temp is None or temp[0] is not int:
            return 0
        return int(*temp)

    def delete(self, vaccine_id):
        c = self._conn.cursor()
        c.execute("""
            DELETE FROM vaccines WHERE id = ?
        """, [vaccine_id])

    def update_quantity(self, vaccine_id, quantity):
        c = self._conn.cursor()
        self._conn.execute("""
                UPDATE vaccines 
                SET quantity = ?
                WHERE id = ?
           """, [quantity, vaccine_id])


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

    def get_id(self, name):
        c = self._conn.cursor()
        c.execute("""
                SELECT id FROM suppliers WHERE name = ?
            """, [name])

        return int(*c.fetchone())

    def get_logistic_by_name(self, name):
        c = self._conn.cursor()
        c.execute("""
                SELECT logistic FROM suppliers WHERE name = ?
            """, [name])

        return str(*c.fetchone())

    def get_logistic_by_id(self, supplier_id):
        c = self._conn.cursor()
        c.execute("""
                SELECT logistic FROM suppliers WHERE id = ?
            """, [supplier_id])

        return str(*c.fetchone())


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
        c = self._conn.cursor()
        c.execute("""
            SELECT demand FROM clinics WHERE location = ?
        """, [location])
        curr_demand = int(*c.fetchone())
        new_demand = max(curr_demand - amount, 0)

        self._conn.execute("""
                UPDATE clinics 
                SET demand = ?
                WHERE location = ?
           """, [new_demand, location])

    def total_demand(self):
        c = self._conn.cursor()
        c.execute("""
            SELECT SUM(demand) FROM clinics
        """)

        return int(*c.fetchone())


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

    def increase_count_received(self, logistic_id, amount):
        self._conn.execute("""
                UPDATE logistics 
                SET count_received = count_received + (?)
                WHERE id = (?)
           """, [amount, logistic_id])

    def increase_count_send(self, logistic_id, amount):
        self._conn.execute("""
                UPDATE logistics 
                SET count_sent = count_sent + (?)
                WHERE id = (?)
           """, [amount, logistic_id])

    def total_received(self):
        c = self._conn.cursor()
        c.execute("""
            SELECT SUM(count_received) FROM logistics
        """)
        return int(*c.fetchone())

    def total_sent(self):
        c = self._conn.cursor()
        c.execute("""
            SELECT SUM(count_sent) FROM logistics
        """)
        return int(*c.fetchone())


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
