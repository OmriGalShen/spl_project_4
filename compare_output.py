import sys
import numpy as np
import itertools
import sqlite3


def output_check():
    cmp = np.array([[int(x) for x in(l.strip('\n').split(','))] for l in open(sys.argv[1])]) == np.array([[int(x) for x in(l.strip('\n').split(','))] for l in open(sys.argv[2])])
    [print(f'Mismatch in line {i} value {j}') for i,j in itertools.product(range(cmp.shape[0]),range(cmp.shape[1])) if cmp[i,j] == False];
    return np.sum(cmp)/cmp.size


def compare(true_lst, tested_lst,lst_name):
    tested_lst = list(tested_lst)
    mismatches = 0    
    for elem in true_lst:
        try:
            tested_lst.remove(elem)
        except ValueError:
            print(f'Mistake in {lst_name}, no match for: {elem}')
            mismatches+=1
    return (len(true_lst)-mismatches)/len(true_lst)


def compare_logstics(db_true,db_tested):
    true_db = db_true.execute("""SELECT log.name, log.count_sent, log.count_received FROM logistics as log""").fetchall()
    tested_db = db_tested.execute("""SELECT log.name, log.count_sent, log.count_received FROM logistics as log""").fetchall()
    return compare(true_db,tested_db,'logistics')

def swap_seperators(lst):
    '''
    lst is either a list of lists or a list of tuples.
    will return a list/tuple where all − occurrences been replaced with - .
    '''
    for j,l in enumerate(lst):
        nl = list(l)
        for i,v in enumerate(nl):
            if isinstance(v,str):
                nl[i] = v.replace('−','-').strip('\n')
        lst[j] = nl if isinstance(l,list) else tuple(nl)
    return lst


def fix_dates(lst):
    '''
    lst is either a list of lists or a list of tuples.
    will return a list/tuple where a dates of YYYY-MM-D been replaced with YYYY-MM-DD
    '''
    for j,l in enumerate(lst):
        nl = list(l)
        for i,v in enumerate(nl):
            if isinstance(v,str) and v.count('-') == 2:
                v = v.split('-')
                v[-1] = '0'+v[-1] if len(v[-1]) == 1 else v[-1]
                nl[i] = '-'.join(v)
        lst[j] = nl if isinstance(l,list) else tuple(nl)
    return lst

def compare_vaccines(db_true,db_tested):
    true_db = db_true.execute("""SELECT vac.date, vac.quantity, sup.name FROM vaccines as vac
        JOIN suppliers as sup
        on vac.supplier = sup.id""").fetchall()
    true_db = fix_dates(swap_seperators(true_db))
    tested_db = db_tested.execute("""SELECT vac.date, vac.quantity, sup.name FROM vaccines as vac
        JOIN suppliers as sup
        on vac.supplier = sup.id""").fetchall()
    tested_db = fix_dates(swap_seperators(tested_db))
    return compare(true_db,tested_db,'vaccines')

def compare_clinics(db_true,db_tested):
    true_db = db_true.execute("""SELECT clin.location, clin.demand, log.name FROM clinics as clin
        JOIN logistics as log
        on clin.logistic = log.id""").fetchall()
    tested_db = db_tested.execute("""SELECT clin.location, clin.demand, log.name FROM clinics as clin
        JOIN logistics as log
        on clin.logistic = log.id""").fetchall()
    return compare(true_db,tested_db,'clinics')


def db_check():
    db_true = sqlite3.connect(sys.argv[3])
    db_tested = sqlite3.connect(sys.argv[4])
    logistics_grade = compare_logstics(db_true,db_tested)
    print(f'Grade for logistics table:{logistics_grade}')
    vaccines_grade = compare_vaccines(db_true,db_tested)
    print(f'Grade for vaccines table:{vaccines_grade}')
    clinics_grade = compare_clinics(db_true,db_tested)
    print(f'Grade for clinics table:{clinics_grade}')
    return 0.4*clinics_grade+0.3*vaccines_grade+0.3*logistics_grade


if __name__ == '__main__':
    print('OUTPUT FILE TEST')
    output_grade = output_check()
    print(f'Grade for output file:{output_grade}')
    print('\nDB FILE TEST')
    db_grade = db_check()
    print(f'Grade for database file:{db_grade}')
    print(f'Total Grade:{db_grade*0.6+output_grade*0.4}')
