# Data Transfer Objects:
class Vaccine:
    def __init__(self, vaccine_id, date, supplier, quantity):
        self.id = vaccine_id
        self.date = date
        self.supplier = supplier
        self.quantity = quantity


class Supplier:
    def __init__(self, supplier_id, name, logistic):
        self.id = supplier_id
        self.name = name
        self.logistic = logistic


class Clinic:
    def __init__(self, clinic_id, location, demand, logistic):
        self.id = clinic_id
        self.location = location
        self.demand = demand
        self.logistic = logistic


class Logistic:
    def __init__(self, logistic_id, name, count_sent, count_received):
        self.id = logistic_id
        self.name = name
        self.count_sent = count_sent
        self.count_received = count_received
