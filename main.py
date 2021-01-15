import os

from persistence import repo
from dto import Vaccine, Supplier, Clinic, Logistic
import sys


def read_config_file(path):
    """ Read config file line by line
        The file is ordered according to this structure:
        <#1>,<#2>,<#3>,<#4>
        <vaccines>
        <suppliers>
        <clinics>
        <logistics> """
    with open(path) as config_file:
        vaccines_count, suppliers_count, clinics_count, logistics_count = [0] * 4
        for ind, line in enumerate(config_file):
            curr_line = line.split(',')
            if ind == 0:  # First line we get the counters for each type
                vaccines_count, suppliers_count, clinics_count, logistics_count = list(map(int, curr_line))
            elif vaccines_count > 0:
                vaccine = Vaccine(int(curr_line[0]), curr_line[1], int(curr_line[2]), int(curr_line[3]))
                repo.vaccines.insert(vaccine)  # Insert to appropriate table
                vaccines_count -= 1
            elif suppliers_count > 0:
                supplier = Supplier(int(curr_line[0]), curr_line[1], int(curr_line[2]))
                repo.suppliers.insert(supplier)  # Insert to appropriate table
                suppliers_count -= 1
            elif clinics_count > 0:
                clinic = Clinic(int(curr_line[0]), curr_line[1], int(curr_line[2]), int(curr_line[3]))
                repo.clinics.insert(clinic)  # Insert to appropriate table
                clinics_count -= 1
            elif logistics_count > 0:
                logistic = Logistic(int(curr_line[0]), curr_line[1], int(curr_line[2]), int(curr_line[3]))
                repo.logistics.insert(logistic)  # Insert to appropriate table
                logistics_count -= 1
            else:
                continue


def read_orders_file(orders_path, output_path):
    with open(orders_path) as orders_file:
        for line in orders_file:
            curr_line = line.split(',')
            if len(curr_line) == 3:  # Receive Shipment
                print("Receive Shipment")
                name, amount, date = curr_line[0], int(curr_line[1]), curr_line[2]
                supplier_id = repo.suppliers.get_id(name)
                logistic_id = repo.suppliers.get_logistic_by_name(name)
                repo.vaccines.insert(Vaccine(0, date, supplier_id, amount))
                repo.logistics.increase_count_received(logistic_id, amount)
                update_output(output_path)
            elif len(curr_line) == 2:  # Send Shipment
                location, amount = curr_line[0], int(curr_line[1])
                actual_amount, suppliers = repo.vaccines.take(amount)
                for supplier, quantity in suppliers:
                    logistic = repo.suppliers.get_logistic_by_id(supplier)
                    repo.logistics.increase_count_send(logistic, quantity)
                repo.clinics.lower_demand(location, actual_amount)
                print("Send Shipment")
                update_output(output_path)
            else:
                continue


def write_output_file(path, line_arg):
    """
        get output file path and add the line
        <total_inventory>,<total_demand>,<total_received>,<total_sent>
    """
    output_line = ','.join(list(map(str, line_arg))) + '\n'
    with open(path, 'a') as output_file:
        output_file.write(output_line)


def update_output(path):
    """ get the Summary of current state of totals and send
        them to be updated in output file"""
    inventory = repo.vaccines.total_inventory()
    demand = repo.clinics.total_demand()
    received = repo.logistics.total_received()
    send = repo.logistics.total_sent()
    write_output_file(path, [inventory, demand, received, send])


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Paths not supplied")
        pass
    config_path, orders_path, output_path = sys.argv[1:]  # get files paths from arguments
    repo.create_tables()  # create Vaccine, Supplier, Clinic, Logistic tables
    read_config_file(config_path)
    read_orders_file(orders_path, output_path)
