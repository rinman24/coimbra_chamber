"""
Plot the P vs. T settings for the tests in the MySQL database.

This script should be called as follows:

   $ python -m chamber.scripts.db_check <database>

Where database is the name of the schema to insert the results into.
"""
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from chamber.data import sqldb, dml

PT_LIST = [(275, 30000), (275, 50000), (275, 70000), (275, 90000),
           (280, 40000), (280, 60000), (280, 80000), (280, 100000),
           (290, 60000), (290, 80000), (290, 100000), (300, 80000),
           (300, 100000), (310, 100000)]


def _get_setting_df(cnx):
    """Get dataframe of settings if MySQL database.

    Use Pandas read_sql function to read a MySQL querry and return a
    `DataFrame` of settings information in the MySQL database.

    Parameters
    ----------
    cnx : mysql.connector.connection.MySQLConnection
        Connection to MySQL database.

    Returns
    -------
    `DataFrame`
        A `DataFrame` of settings infromation in the MySQL database.

    Examples
    --------
    Get the settings infromation from the database.

    >>> cnx = connect('my-schema')
    >>> _get_setting_df(cnx)
       Pressure  Temperature  Reservoir  TestId
    0     40000        280.0          1       1
    1    100000        290.0          0       2
    2     60000        290.0          0       3

    """
    settings = pd.read_sql(dml.settings_df, cnx)
    return settings


def _get_analysis_tid_df(cnx):
    """Get a dataframe of TestIds that have been analyzed.

    Use Pandas read_sql function to read a MySQL querry and return a
    `DataFrame` of TestIds that have been analyzed.

    Parameters
    ----------
    cnx : mysql.connector.connection.MySQLConnection
        Connection to MySQL database.

    Returns
    -------
    `DataFrame`
        A `DataFrame` of TestIds that have been analyzed in the MySQL database.

    Examples
    --------
    Get the TestIds that have been analyzed from the database.

    >>> cnx = connect('my-schema')
    >>> _get_analysis_tid_df(cnx)
        TestId
    0        1
    1        2

    """
    tid_df = pd.read_sql(dml.analysis_tid, cnx)
    return tid_df


def exp_plot(cnx):
    """Plot the P vs. T settings for the tests in the MySQL database.

    Plot the Pressure vs. Temperature settings for the tests currently in the
    MySQL database. Also provides visual feedback denoting which tests are
    analyzed.

    Parameters
    ----------
    cnx : mysql.connector.connection.MySQLConnection
        Connection to MySQL database.

    Returns
    -------
    `True` or `None`
        `True` if sucessful, else `None`.

    Examples
    --------
    Get the TestIds that have been analyzed from the database.

    >>> cnx = connect('my-schema')
    >>> exp_plot(cnx)
    True

    """
    t_max = 313.15
    gamma = 11.4
    p_not = 101325.0
    t = np.linspace(273, 312, 100)
    p = p_not*(t/t_max)**gamma
    plt.plot(t, p)
    sdf = _get_setting_df(cnx)
    for pnt in PT_LIST:
        plt.plot(pnt[0], pnt[1], c='grey', marker='.')
    tid_df = _get_analysis_tid_df(cnx)
    label_list = []
    for tid in sdf.TestId:
        if tid in sdf[sdf.TestId.isin(tid_df.TestId)].TestId.data:
            plt.scatter(
                sdf.loc[(sdf['TestId'] == tid) & (sdf['Reservoir'] == 1),
                        'Temperature'],
                sdf.loc[(sdf['TestId'] == tid) & (sdf['Reservoir'] == 1),
                        'Pressure'],
                c='blue', marker='+', s=300,
                label='HighRH A' if 'HighRH A' not in label_list else '')
            plt.scatter(
                sdf.loc[(sdf['TestId'] == tid) & (sdf['Reservoir'] == 0),
                        'Temperature'],
                sdf.loc[(sdf['TestId'] == tid) & (sdf['Reservoir'] == 0),
                        'Pressure'],
                c='orange', marker='x', s=250,
                label='LowRH A' if 'LowRH A' not in label_list else '')
            if 'HighRH A' not in label_list:
                label_list = label_list + ['HighRH A', 'LowRH A']
        else:
            plt.scatter(
                sdf.loc[(sdf['TestId'] == tid) & (sdf['Reservoir'] == 1),
                        'Temperature'],
                sdf.loc[(sdf['TestId'] == tid) & (sdf['Reservoir'] == 1),
                        'Pressure'],
                c='grey', marker='+', s=300,
                label='HighRH No A' if 'HighRH No A' not in label_list else '')
            plt.scatter(
                sdf.loc[(sdf['TestId'] == tid) & (sdf['Reservoir'] == 0),
                        'Temperature'],
                sdf.loc[(sdf['TestId'] == tid) & (sdf['Reservoir'] == 0),
                        'Pressure'],
                c='grey', marker='x', s=250,
                label='LowRH No A' if 'LowRH No A' not in label_list else '')
            if 'HighRH NA' not in label_list:
                label_list = label_list + ['HighRH No A', 'LowRH No A']
    print(
        'No Analysis TestId:',
        list(sdf[~sdf.TestId.isin(tid_df.TestId)].TestId))
    plt.xlim(273, 312)
    plt.ylim(20000, 102000)
    plt.xlabel('T/K')
    plt.ylabel('P/Pa')
    plt.title('Tests In Database')
    plt.grid()
    plt.legend()
    plt.show()
    return True


def add_analysis(cnx):
    """Propmt user for a Testid to apply and insert analysis into database."""
    add_analysis = input('Add analysis to database? [y/n]')
    if add_analysis == 'y':
        test_id = input('Which TestId would you like to analyze [ex. "3"]')
        print('Adding TestId ', test_id, '...')
        sqldb.add_analysis(cnx, test_id)
        print('Done.')
        return True
    elif add_analysis == 'n':
        print('No analysis added.')
        return False
    else:
        print('Incorrect input, analysis aborted.')
        return False


if __name__ == '__main__':
    schema = sys.argv[1]
    cnx = sqldb.connect(schema)
    exp_plot(cnx)
    add = True
    while add is True:
        add = add_analysis(cnx)
        exp_plot(cnx)
