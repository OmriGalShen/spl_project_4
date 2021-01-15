from persistence import repo
from dto import Vaccine, Supplier, Clinic, Logistic

import os


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("hellow world!")
    repo.create_tables()
    repo.vaccines.insert(Vaccine(1,'2021−01−1', 1, 1))
    # example for calling repo
    # repo.assignments.find(assignment_num)

