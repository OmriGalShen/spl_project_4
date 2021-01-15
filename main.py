from persistence import repo
from dto import Vaccine, Supplier, Clinic, Logistic
import sys


def read_config_file(path):
    with open(path) as config_file:
        vaccines_count, suppliers_count, clinics_count, logistics_count = [0] * 4
        for ind, line in enumerate(config_file):
            curr_line = line.split(',')
            if ind == 0:
                vaccines_count, suppliers_count, clinics_count, logistics_count = list(map(int, curr_line))
            elif vaccines_count > 0:
                vaccine = Vaccine(int(curr_line[0]), curr_line[1], int(curr_line[2]), int(curr_line[3]))
                repo.vaccines.insert(vaccine)
                vaccines_count -= 1
            elif suppliers_count > 0:
                supplier = Supplier(int(curr_line[0]), curr_line[1], int(curr_line[2]))
                repo.suppliers.insert(supplier)
                suppliers_count -= 1
            elif clinics_count > 0:
                clinic = Clinic(int(curr_line[0]), curr_line[1], int(curr_line[2]), int(curr_line[3]))
                repo.clinics.insert(clinic)
                clinics_count -= 1
            elif logistics_count > 0:
                logistic = Logistic(int(curr_line[0]), curr_line[1], int(curr_line[2]), int(curr_line[3]))
                repo.logistics.insert(logistic)
                logistics_count -= 1
            else:
                continue


def read_orders_file(path):
    with open(path) as order_file:
        for line in order_file:
            curr_line = line.split(',')
            if len(curr_line) == 3:  # Receive Shipment
                print("Receive Shipment")
                name, amount, date = curr_line[0], int(curr_line[1]), curr_line[2]
                supplier_id = repo.suppliers.getID(name)
                repo.vaccines.insert(Vaccine(0, date, supplier_id, amount))
            elif len(curr_line) == 2:  # Send Shipment
                location, amount = curr_line[0], int(curr_line[1])
                print("Send Shipment")
            else:
                continue


def write_output_file(path, line_arg):
    output_line = ','.join(list(map(str, line_arg))) + '\n'
    with open(path, 'a') as output_file:
        output_file.write(output_line)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Paths not supplied")
        pass
    config_path, order_path, output_path = sys.argv[1:]
    print("hello world!")
    repo.create_tables()
    read_config_file(config_path)
    read_orders_file(order_path)
    # print(f"current: {repo.vaccines.find(1).quantity}")
    # repo.vaccines.take(1, 20)
    # print(f"current: {repo.vaccines.find(1).quantity}")
    # repo.vaccines.add(1, 30)
    # print(f"current: {repo.vaccines.find(1).quantity}")

    write_output_file(output_path, [1, 1, 1, 1])
    write_output_file(output_path, [1, 2, 3, 4])
    write_output_file(output_path, [5, 6, 7, 8])
