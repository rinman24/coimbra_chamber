"""Experiment access module."""

import chamber.utilities.ddl as ddl
import mysql.connector


def build_experiment_tables(cursor):
    for table in ddl.build_instructions['experiments', 'table order']:
        try:
            print('Creating table {}: '.format(table), end='')
            cursor.execute(
               ddl.build_instructions['experiments', 'ddl'][table]
               )
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_TABLE_EXISTS_ERROR:
                print('already exists.')
            else:
                print(err.msg)
        else:
            print('OK')