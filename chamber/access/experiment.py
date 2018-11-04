"""Experiment access module."""

import chamber.utilities.ddl as ddl


def build_experiment_tables(cursor):
    for table in ddl.build_instructions['experiments', 'table order']:
        print('Building table: {}...'.format(table), end=' ')
        cursor.execute(ddl.build_instructions['experiments', 'ddl'][table])
        print('done')
