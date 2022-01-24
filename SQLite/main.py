import sqlite3
import matplotlib.pyplot as plt
import os


def download_data():
    os.system('wget https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/breast-cancer-wisconsin.data')
    # os.system('wget https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/breast-cancer-wisconsin.names')



def data_generator(file):
    with open(file, 'r') as f:
        for line in f.readlines():
            items = line.split(',')
            if any([x == '?' for x in items]):
                continue
            items = [int(x) for x in items]
            yield tuple(items)



def write_to_database(cols, csv_file, db_name='test.db', ):
    entries = [f"'{x}' int," for x in cols]
    create_vars_command = ''.join(entries)
    create_vars_command = create_vars_command[:-1]
    print(create_vars_command)

    with sqlite3.connect(db_name) as con:
        c = con.cursor()

        c.execute(f'''
        CREATE TABLE if NOT EXISTS information
        ({create_vars_command})
        ''')

        for x in data_generator(csv_file):
            c.execute(f'''
            INSERT INTO information VALUES
            {x}
            ''')

        con.commit()



def read_database(variable, value, db_name='test.db'):
    print(f'selecting all entries from database {db_name} where "{variable}" == {value}')
    with sqlite3.connect(db_name) as con:
        c = con.cursor()
        for row in c.execute(f'''SELECT * FROM information WHERE "{variable}" is {value}'''):
            print(row)



if __name__ == '__main__':
    columns = ['Sample code number', 'Clump Thickness', 'Uniformity of Cell Size', 'Uniformity of Cell Shape',
               'Marginal Adhesion', 'Single Epithelial Cell Size', 'Bare Nuclei',
               'Bland Chromatin', 'Normal Nucleoli', 'Mitoses', 'Class']
    data_file = 'breast-cancer-wisconsin.data'
    if not os.path.exists(data_file):
        download_data()

    # write_to_database(cols=columns, csv_file=data_file)
    # read_database(variable='Class', value=2)


    with sqlite3.connect('test.db') as con:
        c = con.cursor()
        for col in columns[1:10]:
            print(col)
            good = [x[0] for x in c.execute(f'''SELECT "{col}" FROM information WHERE "Class" is 2''')]
            bad = [x[0] for x in c.execute(f'''SELECT "{col}" FROM information WHERE "Class" is 4''')]

            plt.hist(good, bins=10, color='green', alpha=0.5)
            plt.hist(bad, bins=10, color='red', alpha=0.5)
            plt.suptitle(col)
            plt.show()


